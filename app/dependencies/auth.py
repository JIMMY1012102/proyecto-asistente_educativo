"""
Dependencies de FastAPI para control de acceso y autenticación.

Este módulo define las dependencies que se usan en los endpoints
para verificar autenticación, roles y permisos específicos.

Valida: Requisitos 1.1, 1.3, 1.4, 1.5, 1.6, 1.7
"""

from typing import Optional, List
from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.models.auth import UsuarioAutenticado, AccesoNoAutorizadoError, CredencialesInvalidasError
from app.models.enums import Rol
from app.utils.auth import (
    verificar_token_jwt, verificar_acceso_rol, verificar_acceso_estudiante_propio,
    verificar_acceso_direccion_agregado
)


# Security scheme para documentación automática de FastAPI
security = HTTPBearer(auto_error=False)


async def get_usuario_actual(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> UsuarioAutenticado:
    """
    Dependency para obtener el usuario autenticado actual.
    
    Extrae el usuario del state del request (añadido por el middleware)
    o valida el token directamente si el middleware no está activo.
    
    Args:
        request: Request de FastAPI
        credentials: Credenciales HTTP Bearer (para documentación)
        
    Returns:
        UsuarioAutenticado con información del token JWT
        
    Raises:
        HTTPException: Si no hay autenticación válida
        
    Valida: Requisitos 1.3, 1.4
    """
    # Intentar obtener usuario del middleware primero
    if hasattr(request.state, 'usuario') and request.state.usuario:
        return request.state.usuario
    
    # Fallback: validar token directamente si no hay middleware
    if not credentials or not credentials.credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere autenticación. Por favor, incluya un token JWT válido.",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    try:
        return verificar_token_jwt(credentials.credentials)
    except CredencialesInvalidasError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token JWT inválido. Por favor, inicie sesión nuevamente.",
            headers={"WWW-Authenticate": "Bearer"}
        )


async def get_usuario_opcional(
    request: Request,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)
) -> Optional[UsuarioAutenticado]:
    """
    Dependency para obtener el usuario autenticado si está presente.
    
    Similar a get_usuario_actual pero no lanza excepción si no hay autenticación.
    
    Args:
        request: Request de FastAPI
        credentials: Credenciales HTTP Bearer opcionales
        
    Returns:
        UsuarioAutenticado si hay token válido, None en caso contrario
    """
    # Intentar obtener usuario del middleware
    if hasattr(request.state, 'usuario'):
        return request.state.usuario
    
    # Intentar validar token si está presente
    if credentials and credentials.credentials:
        try:
            return verificar_token_jwt(credentials.credentials)
        except (CredencialesInvalidasError, Exception):
            return None
    
    return None


def require_role(rol_requerido: Rol, recurso: str = ""):
    """
    Factory para crear dependency que requiere un rol específico.
    
    Args:
        rol_requerido: Rol mínimo requerido
        recurso: Descripción del recurso (opcional)
        
    Returns:
        Dependency que valida el rol del usuario
        
    Valida: Requisitos 1.5, 1.6, 1.7
    """
    async def _verificar_rol(
        usuario: UsuarioAutenticado = Depends(get_usuario_actual)
    ) -> UsuarioAutenticado:
        try:
            verificar_acceso_rol(usuario, rol_requerido, recurso)
            return usuario
        except AccesoNoAutorizadoError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
    
    return _verificar_rol


def require_estudiante(
    usuario: UsuarioAutenticado = Depends(get_usuario_actual)
) -> UsuarioAutenticado:
    """
    Dependency que requiere rol de Estudiante.
    
    Valida: Requisito 1.5
    """
    try:
        verificar_acceso_rol(usuario, Rol.ESTUDIANTE, "recursos de estudiante")
        return usuario
    except AccesoNoAutorizadoError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


def require_docente(
    usuario: UsuarioAutenticado = Depends(get_usuario_actual)
) -> UsuarioAutenticado:
    """
    Dependency que requiere rol de Docente o superior.
    
    Valida: Requisito 1.6
    """
    try:
        verificar_acceso_rol(usuario, Rol.DOCENTE, "recursos de docente")
        return usuario
    except AccesoNoAutorizadoError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


def require_direccion(
    usuario: UsuarioAutenticado = Depends(get_usuario_actual)
) -> UsuarioAutenticado:
    """
    Dependency que requiere rol de Dirección.
    
    Valida: Requisito 1.7
    """
    try:
        verificar_acceso_rol(usuario, Rol.DIRECCION, "recursos de dirección")
        return usuario
    except AccesoNoAutorizadoError as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e)
        )


def verify_estudiante_access(estudiante_id: int):
    """
    Factory para crear dependency que verifica acceso a datos de estudiante específico.
    
    Args:
        estudiante_id: ID del estudiante
        
    Returns:
        Dependency que verifica permisos de acceso
        
    Valida: Requisitos 1.5, 1.6
    """
    async def _verificar_acceso_estudiante(
        usuario: UsuarioAutenticado = Depends(get_usuario_actual)
    ) -> UsuarioAutenticado:
        try:
            # Verificar que estudiantes solo accedan a sus propios datos
            verificar_acceso_estudiante_propio(usuario, estudiante_id)
            
            # TODO: Verificar que docentes solo accedan a estudiantes de sus grupos
            # Esto requiere consulta a la base de datos para obtener grupos del docente
            # if usuario.rol == Rol.DOCENTE:
            #     grupos_docente = await get_grupos_docente(usuario.usuario_id)
            #     verificar_acceso_docente_grupo(usuario, estudiante_id, grupos_docente)
            
            return usuario
            
        except AccesoNoAutorizadoError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
    
    return _verificar_acceso_estudiante


def verify_no_individual_access():
    """
    Dependency que verifica que la dirección no acceda a datos individuales.
    
    Valida: Requisito 1.7
    """
    async def _verificar_no_acceso_individual(
        usuario: UsuarioAutenticado = Depends(get_usuario_actual)
    ) -> UsuarioAutenticado:
        try:
            verificar_acceso_direccion_agregado(usuario, acceso_individual=True)
            return usuario
        except AccesoNoAutorizadoError as e:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=str(e)
            )
    
    return _verificar_no_acceso_individual


def get_current_estudiante_id(
    usuario: UsuarioAutenticado = Depends(require_estudiante)
) -> int:
    """
    Dependency que retorna el ID del estudiante autenticado.
    
    Útil para endpoints que necesitan el ID del estudiante actual.
    
    Args:
        usuario: Usuario autenticado (debe ser estudiante)
        
    Returns:
        ID del estudiante actual
        
    Valida: Requisito 1.5
    """
    return usuario.usuario_id


def get_current_docente_id(
    usuario: UsuarioAutenticado = Depends(require_docente)
) -> int:
    """
    Dependency que retorna el ID del docente autenticado.
    
    Útil para endpoints que necesitan el ID del docente actual.
    
    Args:
        usuario: Usuario autenticado (debe ser docente o superior)
        
    Returns:
        ID del docente actual
        
    Valida: Requisito 1.6
    """
    return usuario.usuario_id


class RoleChecker:
    """
    Clase para crear dependencies de verificación de roles más complejas.
    
    Permite múltiples roles y validaciones adicionales.
    """
    
    def __init__(self, allowed_roles: List[Rol], recurso: str = ""):
        """
        Inicializa el verificador de roles.
        
        Args:
            allowed_roles: Lista de roles permitidos
            recurso: Descripción del recurso
        """
        self.allowed_roles = allowed_roles
        self.recurso = recurso
    
    def __call__(self, usuario: UsuarioAutenticado = Depends(get_usuario_actual)) -> UsuarioAutenticado:
        """
        Verifica si el usuario tiene alguno de los roles permitidos.
        
        Args:
            usuario: Usuario autenticado
            
        Returns:
            Usuario autenticado si tiene acceso
            
        Raises:
            HTTPException: Si el usuario no tiene ninguno de los roles permitidos
        """
        if usuario.rol not in self.allowed_roles:
            roles_str = ", ".join([rol.value for rol in self.allowed_roles])
            mensaje = f"Se requiere uno de los siguientes roles: {roles_str}"
            if self.recurso:
                mensaje += f" para acceder a {self.recurso}"
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=mensaje
            )
        
        return usuario


# Dependencies preconfiguradas comunes
require_docente_o_direccion = RoleChecker(
    [Rol.DOCENTE, Rol.DIRECCION], 
    "recursos administrativos"
)

require_cualquier_rol = RoleChecker(
    [Rol.ESTUDIANTE, Rol.DOCENTE, Rol.DIRECCION],
    "sistema"
)