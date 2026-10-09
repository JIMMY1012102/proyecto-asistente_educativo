"""
Router de autenticación para el sistema CNI.

Este módulo define los endpoints de autenticación:
- Login de usuarios
- Verificación de tokens
- Logout de usuarios

Valida: Requisitos 1.1, 1.2, 1.3, 1.4
"""

from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer

from app.models.auth import CredencialesLogin, TokenResponse, UsuarioAutenticado
from app.services.auth_service import authenticate_user_login, logout_user
from app.dependencies.auth import get_usuario_actual
from app.models.auth import CredencialesInvalidasError


router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"],
    responses={
        401: {"description": "Credenciales inválidas"},
        403: {"description": "Acceso no autorizado"}
    }
)

security = HTTPBearer()


@router.post("/login", response_model=TokenResponse)
async def login(credenciales: CredencialesLogin):
    """
    Autentica un usuario y retorna un token JWT.
    
    Este endpoint valida las credenciales del usuario contra la base de datos
    y genera un token JWT válido por 8 horas si la autenticación es exitosa.
    
    Args:
        credenciales: Credenciales de login (username y password)
        
    Returns:
        TokenResponse con token JWT, tipo de token, tiempo de expiración y rol
        
    Raises:
        HTTPException 401: Si las credenciales son incorrectas
        HTTPException 500: Si hay error interno durante autenticación
        
    Valida: Requisitos 1.1, 1.2
    """
    try:
        token_response = await authenticate_user_login(credenciales)
        return token_response
        
    except CredencialesInvalidasError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas",
            headers={"WWW-Authenticate": "Bearer"}
        )
    except Exception as e:
        # Log del error interno para debugging
        # TODO: Implementar logging apropiado
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error interno durante la autenticación"
        )


@router.get("/me", response_model=UsuarioAutenticado)
async def get_user_info(usuario: UsuarioAutenticado = Depends(get_usuario_actual)):
    """
    Obtiene información del usuario autenticado actual.
    
    Este endpoint retorna los datos del usuario extraídos del token JWT,
    útil para verificar que el token es válido y obtener información del usuario.
    
    Args:
        usuario: Usuario autenticado (extraído del token JWT)
        
    Returns:
        UsuarioAutenticado con información completa del usuario
        
    Requires:
        Header Authorization: Bearer <token_jwt>
        
    Valida: Requisitos 1.3, 1.4
    """
    return usuario


@router.post("/logout")
async def logout(usuario: UsuarioAutenticado = Depends(get_usuario_actual)):
    """
    Cierra sesión del usuario autenticado.
    
    En la implementación actual, simplemente verifica que el token sea válido.
    En una implementación con base de datos, esto añadiría el token a una lista negra.
    
    Args:
        usuario: Usuario autenticado (extraído del token JWT)
        
    Returns:
        Mensaje de confirmación de logout
        
    Requires:
        Header Authorization: Bearer <token_jwt>
        
    Valida: Requisito 1.4
    """
    try:
        # En una implementación real, extraeríamos el token del header
        # Por ahora, simplemente confirmamos que el usuario está autenticado
        success = await logout_user(f"placeholder_token_for_user_{usuario.usuario_id}")
        
        return {
            "message": "Logout exitoso",
            "usuario": usuario.nombre_usuario,
            "success": success
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error durante el logout"
        )


@router.get("/verify")
async def verify_token(usuario: UsuarioAutenticado = Depends(get_usuario_actual)):
    """
    Verifica que el token JWT actual sea válido.
    
    Endpoint simple para verificar la validez de un token sin retornar
    información completa del usuario.
    
    Args:
        usuario: Usuario autenticado (extraído del token JWT)
        
    Returns:
        Confirmación de token válido
        
    Requires:
        Header Authorization: Bearer <token_jwt>
        
    Valida: Requisitos 1.3, 1.4
    """
    return {
        "valid": True,
        "message": "Token JWT válido",
        "usuario_id": usuario.usuario_id,
        "rol": usuario.rol.value,
        "expires_in": "8 horas desde emisión"
    }


# Endpoints de desarrollo/testing (solo en modo DEBUG)
@router.get("/test/usuarios")
async def get_test_users():
    """
    Lista usuarios disponibles para testing.
    
    SOLO DISPONIBLE EN MODO DEBUG.
    
    Returns:
        Lista de usuarios simulados disponibles
    """
    from app.services.auth_service import auth_service
    import os
    
    if os.getenv("DEBUG", "False").lower() != "true":
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Endpoint no disponible"
        )
    
    usuarios = auth_service.get_usuarios_disponibles()
    return {
        "usuarios_disponibles": usuarios,
        "note": "Usar password 'password123' para estudiantes, 'docente123' para docentes, 'direccion123' para dirección"
    }