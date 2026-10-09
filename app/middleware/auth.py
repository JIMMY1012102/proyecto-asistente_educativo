"""
Middleware de autenticación para FastAPI.

Este módulo implementa el middleware que valida tokens JWT en cada request
y maneja la autenticación automática para endpoints protegidos.

Valida: Requisitos 1.3, 1.4
"""

from typing import Callable
from fastapi import Request, Response, HTTPException, status
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.utils.auth import verificar_token_jwt, extraer_token_bearer
from app.models.auth import TokenExpiradoError, CredencialesInvalidasError


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware de autenticación JWT para validar tokens en cada request.
    
    Valida tokens JWT automáticamente en endpoints protegidos y
    añade información del usuario autenticado al state del request.
    
    Valida: Requisitos 1.3, 1.4
    """
    
    def __init__(self, app, exclude_paths: list = None):
        """
        Inicializa el middleware de autenticación.
        
        Args:
            app: Aplicación FastAPI
            exclude_paths: Lista de paths que no requieren autenticación
        """
        super().__init__(app)
        
        # Paths que no requieren autenticación
        self.exclude_paths = exclude_paths or [
            "/",
            "/health",
            "/docs",
            "/redoc",
            "/openapi.json",
            "/auth/login",
            "/static"
        ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesa cada request validando autenticación cuando es necesaria.
        
        Args:
            request: Request HTTP entrante
            call_next: Siguiente middleware o endpoint
            
        Returns:
            Response del endpoint o error de autenticación
            
        Valida: Requisitos 1.3, 1.4
        """
        # Verificar si el path está excluido de autenticación
        if self._is_excluded_path(request.url.path):
            return await call_next(request)
        
        # Verificar si es un path estático
        if request.url.path.startswith("/static/"):
            return await call_next(request)
        
        try:
            # Extraer token del header Authorization
            authorization = request.headers.get("Authorization")
            if not authorization:
                return self._unauthorized_response("Header Authorization faltante")
            
            # Extraer y verificar token JWT
            token = extraer_token_bearer(authorization)
            usuario_autenticado = verificar_token_jwt(token)
            
            # Añadir usuario autenticado al state del request
            request.state.usuario = usuario_autenticado
            request.state.token_valido = True
            
            # Continuar con el siguiente middleware/endpoint
            response = await call_next(request)
            return response
            
        except TokenExpiradoError as e:
            return self._unauthorized_response(
                "Token expirado. Por favor, inicie sesión nuevamente.",
                error_code="TOKEN_EXPIRED"
            )
            
        except CredencialesInvalidasError as e:
            return self._unauthorized_response(
                "Token inválido. Por favor, inicie sesión nuevamente.",
                error_code="INVALID_TOKEN"
            )
            
        except Exception as e:
            # Log del error interno (no exponer detalles al cliente)
            return self._unauthorized_response(
                "Error de autenticación. Por favor, inicie sesión nuevamente.",
                error_code="AUTH_ERROR"
            )
    
    def _is_excluded_path(self, path: str) -> bool:
        """
        Verifica si un path está excluido de autenticación.
        
        Args:
            path: Path del request
            
        Returns:
            True si el path está excluido
        """
        # Normalizar path
        normalized_path = path.rstrip("/") if path != "/" else path
        
        # Verificar paths exactos
        if normalized_path in self.exclude_paths:
            return True
        
        # Verificar paths con prefijo (como /static/*)
        for exclude_path in self.exclude_paths:
            if exclude_path.endswith("*") or exclude_path.endswith("/"):
                prefix = exclude_path.rstrip("*").rstrip("/")
                if normalized_path.startswith(prefix):
                    return True
        
        return False
    
    def _unauthorized_response(self, message: str, error_code: str = "UNAUTHORIZED") -> JSONResponse:
        """
        Crea una respuesta de error de autenticación estandarizada.
        
        Args:
            message: Mensaje de error
            error_code: Código de error específico
            
        Returns:
            JSONResponse con error 401
            
        Valida: Requisito 1.2 (mensaje genérico sin revelar detalles)
        """
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={
                "error": error_code,
                "message": message,
                "detail": "Se requiere autenticación válida para acceder a este recurso"
            },
            headers={"WWW-Authenticate": "Bearer"}
        )


class OptionalAuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware de autenticación opcional que permite requests sin token
    pero valida el token si está presente.
    
    Útil para endpoints que pueden funcionar con o sin autenticación.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Procesa request con autenticación opcional.
        
        Args:
            request: Request HTTP entrante
            call_next: Siguiente middleware o endpoint
            
        Returns:
            Response del endpoint
        """
        # Inicializar state por defecto
        request.state.usuario = None
        request.state.token_valido = False
        
        # Intentar autenticación si hay header Authorization
        authorization = request.headers.get("Authorization")
        if authorization:
            try:
                token = extraer_token_bearer(authorization)
                usuario_autenticado = verificar_token_jwt(token)
                
                # Añadir usuario al state si el token es válido
                request.state.usuario = usuario_autenticado
                request.state.token_valido = True
                
            except (TokenExpiradoError, CredencialesInvalidasError):
                # Ignorar errores de token - el endpoint decidirá si es necesario
                pass
        
        return await call_next(request)