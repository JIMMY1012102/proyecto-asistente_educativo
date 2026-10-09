"""
Utilidades del sistema CNI.

Este paquete contiene funciones de utilidad compartidas entre módulos,
incluyendo configuración, autenticación, logging y helpers generales.
"""

from .config import get_settings, Settings
from .auth import (
    crear_token_jwt, verificar_token_jwt, autenticar_usuario,
    verificar_acceso_rol, verificar_acceso_estudiante_propio,
    verificar_acceso_docente_grupo, verificar_acceso_direccion_agregado,
    extraer_token_bearer, hash_password
)

__all__ = [
    "get_settings", "Settings",
    "crear_token_jwt", "verificar_token_jwt", "autenticar_usuario",
    "verificar_acceso_rol", "verificar_acceso_estudiante_propio",
    "verificar_acceso_docente_grupo", "verificar_acceso_direccion_agregado",
    "extraer_token_bearer", "hash_password"
]