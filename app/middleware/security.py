"""
Middleware de seguridad para la aplicación.

Este módulo implementa middleware de seguridad incluyendo headers de seguridad,
rate limiting básico y validación de requests.
"""

import time
from collections import defaultdict
from typing import Dict, Tuple

from fastapi import FastAPI, Request, Response
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import settings


class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware que añade headers de seguridad a todas las respuestas."""
    
    async def dispatch(self, request: Request, call_next):
        """
        Procesa el request y añade headers de seguridad a la respuesta.
        
        Args:
            request: Request HTTP entrante.
            call_next: Siguiente middleware en la cadena.
            
        Returns:
            Response con headers de seguridad añadidos.
        """
        response = await call_next(request)
        
        # Headers de seguridad básicos
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # CSP básico para prevenir XSS
        csp_policy = (
            "default-src 'self'; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' data: https:; "
            "font-src 'self'; "
            "connect-src 'self'; "
            "frame-ancestors 'none';"
        )
        response.headers["Content-Security-Policy"] = csp_policy
        
        # Header para desarrollo vs producción
        if not settings.is_production:
            response.headers["X-Environment"] = settings.environment
        else:
            # En producción, no exponer información del entorno
            response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        
        return response


class BasicRateLimitMiddleware(BaseHTTPMiddleware):
    """
    Middleware básico de rate limiting por IP.
    
    Note: En producción se recomienda usar un proxy reverso como nginx
    o un servicio especializado como Redis para rate limiting distribuido.
    """
    
    def __init__(self, app, max_requests: int = 100, window_seconds: int = 60):
        """
        Inicializa el middleware de rate limiting.
        
        Args:
            app: Aplicación FastAPI.
            max_requests: Número máximo de requests por ventana.
            window_seconds: Duración de la ventana en segundos.
        """
        super().__init__(app)
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests: Dict[str, list] = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        """
        Procesa el request aplicando rate limiting.
        
        Args:
            request: Request HTTP entrante.
            call_next: Siguiente middleware en la cadena.
            
        Returns:
            Response o error 429 si se excede el rate limit.
        """
        # Obtener IP del cliente
        client_ip = request.client.host if request.client else "unknown"
        
        # Limpiar requests antiguos
        current_time = time.time()
        self.requests[client_ip] = [
            req_time for req_time in self.requests[client_ip]
            if current_time - req_time < self.window_seconds
        ]
        
        # Verificar rate limit
        if len(self.requests[client_ip]) >= self.max_requests:
            return Response(
                content="Rate limit exceeded. Try again later.",
                status_code=429,
                headers={
                    "Retry-After": str(self.window_seconds),
                    "X-RateLimit-Limit": str(self.max_requests),
                    "X-RateLimit-Remaining": "0",
                    "X-RateLimit-Reset": str(int(current_time + self.window_seconds))
                }
            )
        
        # Registrar este request
        self.requests[client_ip].append(current_time)
        
        # Continuar con el request
        response = await call_next(request)
        
        # Añadir headers informativos sobre rate limiting
        remaining = self.max_requests - len(self.requests[client_ip])
        response.headers["X-RateLimit-Limit"] = str(self.max_requests)
        response.headers["X-RateLimit-Remaining"] = str(remaining)
        response.headers["X-RateLimit-Reset"] = str(int(current_time + self.window_seconds))
        
        return response


def configure_security_middleware(app: FastAPI) -> None:
    """
    Configura todos los middlewares de seguridad para la aplicación.
    
    Args:
        app: Instancia de la aplicación FastAPI.
    """
    # Trusted Host middleware para prevenir ataques de Host header
    if settings.is_production:
        allowed_hosts = ["localhost", "127.0.0.1"]
        if settings.cors_origins_list:
            # Extraer hosts de las URLs de CORS permitidas
            for origin in settings.cors_origins_list:
                if "://" in origin:
                    host = origin.split("://")[1].split(":")[0]
                    allowed_hosts.append(host)
        
        app.add_middleware(TrustedHostMiddleware, allowed_hosts=allowed_hosts)
    
    # Rate limiting básico
    app.add_middleware(
        BasicRateLimitMiddleware,
        max_requests=100 if settings.is_production else 1000,  # Más permisivo en desarrollo
        window_seconds=60
    )
    
    # Headers de seguridad
    app.add_middleware(SecurityHeadersMiddleware)