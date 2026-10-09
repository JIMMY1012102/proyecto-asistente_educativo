"""
Dependencias de FastAPI.

Este módulo contiene las dependencias reutilizables para validación
de autenticación y roles de usuario.
"""

from .auth import (
    get_usuario_actual, get_usuario_opcional,
    require_role, require_estudiante, require_docente, require_direccion,
    verify_estudiante_access, verify_no_individual_access,
    get_current_estudiante_id, get_current_docente_id,
    RoleChecker, require_docente_o_direccion, require_cualquier_rol,
    security
)

__all__ = [
    "get_usuario_actual", "get_usuario_opcional",
    "require_role", "require_estudiante", "require_docente", "require_direccion",
    "verify_estudiante_access", "verify_no_individual_access",
    "get_current_estudiante_id", "get_current_docente_id",
    "RoleChecker", "require_docente_o_direccion", "require_cualquier_rol",
    "security"
]