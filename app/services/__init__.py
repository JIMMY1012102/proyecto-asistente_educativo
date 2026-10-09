"""
Servicios de lógica de negocio del sistema CNI.

Este paquete contiene los servicios que implementan la lógica de negocio
principal del sistema, incluyendo autenticación, reportes y cálculos.
"""

from .auth_service import (
    AuthService, auth_service, 
    authenticate_user_login, verify_user_token, logout_user
)

__all__ = [
    "AuthService", "auth_service",
    "authenticate_user_login", "verify_user_token", "logout_user"
]