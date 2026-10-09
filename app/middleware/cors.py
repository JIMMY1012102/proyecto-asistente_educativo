"""
Configuración de CORS para FastAPI.

Este módulo configura el middleware CORS siguiendo las mejores prácticas
de seguridad y los requisitos de la aplicación.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings


def configure_cors(app: FastAPI) -> None:
    """
    Configura el middleware CORS para la aplicación FastAPI.
    
    Args:
        app: Instancia de la aplicación FastAPI.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=settings.cors_allow_credentials,
        allow_methods=settings.cors_methods_list,
        allow_headers=settings.cors_allow_headers.split(",") if settings.cors_allow_headers != "*" else ["*"],
        expose_headers=["Content-Length", "Content-Type"],
        max_age=600,  # 10 minutos de cache para preflight requests
    )