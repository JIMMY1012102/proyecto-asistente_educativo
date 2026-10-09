"""
Routers de la API FastAPI para el sistema CNI.

Este paquete contiene todos los routers que definen los endpoints
de la API REST, organizados por funcionalidad y rol de usuario.
"""

from .auth import router as auth_router

__all__ = [
    "auth_router"
]