"""
Servicio de autenticación para el sistema CNI.

Este módulo orquesta la lógica de autenticación de usuarios,
incluyendo login, validación de tokens y manejo de sesiones.

Valida: Requisitos 1.1, 1.2, 1.3, 1.4
"""

import os
from typing import Dict, Any, Optional
from datetime import datetime

from app.models.auth import (
    CredencialesLogin, TokenResponse, UsuarioAutenticado, RegistroAcceso,
    CredencialesInvalidasError, TokenExpiradoError
)
from app.models.enums import Rol
from app.utils.auth import (
    autenticar_usuario, crear_token_jwt, verificar_token_jwt, hash_password
)


class AuthService:
    """
    Servicio principal de autenticación del sistema.
    
    Maneja toda la lógica relacionada con autenticación de usuarios,
    creación de tokens JWT y validación de sesiones.
    
    Valida: Requisitos 1.1, 1.2, 1.3, 1.4
    """
    
    def __init__(self):
        """Inicializa el servicio de autenticación."""
        self._usuarios_db = self._cargar_usuarios_simulados()
    
    def _cargar_usuarios_simulados(self) -> Dict[str, Any]:
        """
        Carga usuarios simulados para desarrollo y testing.
        
        En un entorno real, esto se conectaría a la base de datos.
        
        Returns:
            Diccionario con usuarios simulados
            
        Valida: Requisito 11.1 (solo datos simulados)
        """
        return {
            # Estudiantes simulados
            "estudiante01": {
                "usuario_id": 1,
                "password_hash": hash_password("password123"),
                "rol": Rol.ESTUDIANTE.value,
                "codigo_anonimo": "EST-2024-001",
                "activo": True,
                "fecha_creacion": "2024-01-15T08:00:00"
            },
            "estudiante02": {
                "usuario_id": 2,
                "password_hash": hash_password("password123"),
                "rol": Rol.ESTUDIANTE.value,
                "codigo_anonimo": "EST-2024-002",
                "activo": True,
                "fecha_creacion": "2024-01-15T08:00:00"
            },
            "estudiante03": {
                "usuario_id": 3,
                "password_hash": hash_password("password123"),
                "rol": Rol.ESTUDIANTE.value,
                "codigo_anonimo": "EST-2024-003",
                "activo": True,
                "fecha_creacion": "2024-01-15T08:00:00"
            },
            
            # Docentes simulados
            "docente01": {
                "usuario_id": 101,
                "password_hash": hash_password("docente123"),
                "rol": Rol.DOCENTE.value,
                "codigo_anonimo": None,
                "activo": True,
                "fecha_creacion": "2024-01-10T08:00:00"
            },
            "docente02": {
                "usuario_id": 102,
                "password_hash": hash_password("docente123"),
                "rol": Rol.DOCENTE.value,
                "codigo_anonimo": None,
                "activo": True,
                "fecha_creacion": "2024-01-10T08:00:00"
            },
            
            # Dirección simulada
            "direccion": {
                "usuario_id": 201,
                "password_hash": hash_password("direccion123"),
                "rol": Rol.DIRECCION.value,
                "codigo_anonimo": None,
                "activo": True,
                "fecha_creacion": "2024-01-05T08:00:00"
            },
            
            # Usuario inactivo para testing
            "inactivo": {
                "usuario_id": 999,
                "password_hash": hash_password("inactivo123"),
                "rol": Rol.ESTUDIANTE.value,
                "codigo_anonimo": "EST-INACTIVO",
                "activo": False,
                "fecha_creacion": "2024-01-01T08:00:00"
            }
        }
    
    async def login(self, credenciales: CredencialesLogin) -> TokenResponse:
        """
        Autentica un usuario y genera un token JWT.
        
        Args:
            credenciales: Credenciales de login del usuario
            
        Returns:
            TokenResponse con token JWT y metadatos
            
        Raises:
            CredencialesInvalidasError: Si las credenciales son incorrectas
            
        Valida: Requisitos 1.1, 1.2
        """
        try:
            # Autenticar usuario contra la base de datos simulada
            usuario_autenticado = autenticar_usuario(credenciales, self._usuarios_db)
            
            if not usuario_autenticado:
                raise CredencialesInvalidasError("Credenciales incorrectas")
            
            # Generar token JWT
            token_response = crear_token_jwt(usuario_autenticado)
            
            # Registrar login exitoso (sin logging implementado por ahora)
            # TODO: Implementar logging de auditoría
            
            return token_response
            
        except CredencialesInvalidasError:
            # Re-lanzar error de credenciales
            raise
        except Exception as e:
            # Convertir cualquier otro error en error de credenciales genérico
            raise CredencialesInvalidasError("Error durante la autenticación")
    
    async def verificar_token(self, token: str) -> UsuarioAutenticado:
        """
        Verifica un token JWT y retorna el usuario autenticado.
        
        Args:
            token: Token JWT a verificar
            
        Returns:
            UsuarioAutenticado con información del token
            
        Raises:
            TokenExpiradoError: Si el token ha expirado
            CredencialesInvalidasError: Si el token es inválido
            
        Valida: Requisitos 1.3, 1.4
        """
        try:
            usuario = verificar_token_jwt(token)
            
            # Verificar que el usuario sigue activo en la base de datos
            usuario_db = self._usuarios_db.get(usuario.nombre_usuario)
            if not usuario_db or not usuario_db.get("activo", False):
                raise CredencialesInvalidasError("Usuario inactivo")
            
            return usuario
            
        except (TokenExpiradoError, CredencialesInvalidasError):
            # Re-lanzar errores específicos
            raise
        except Exception as e:
            # Convertir otros errores en error genérico
            raise CredencialesInvalidasError(f"Error verificando token: {str(e)}")
    
    async def logout(self, token: str) -> bool:
        """
        Invalida un token JWT (logout).
        
        Args:
            token: Token JWT a invalidar
            
        Returns:
            True si el logout fue exitoso
            
        Note:
            En una implementación con base de datos, esto podría añadir
            el token a una lista negra hasta su expiración natural.
            Por ahora, simplemente verificamos que el token sea válido.
            
        Valida: Requisito 1.4
        """
        try:
            # Verificar que el token es válido antes del logout
            await self.verificar_token(token)
            
            # TODO: Añadir token a lista negra en implementación real
            # TODO: Registrar evento de logout
            
            return True
            
        except (TokenExpiradoError, CredencialesInvalidasError):
            # Token inválido - logout considerado exitoso
            return True
    
    def get_usuarios_disponibles(self) -> Dict[str, str]:
        """
        Retorna lista de usuarios disponibles para testing.
        
        SOLO PARA DESARROLLO - NO usar en producción.
        
        Returns:
            Diccionario con username -> rol para testing
        """
        if os.getenv("DEBUG", "False").lower() != "true":
            return {}
        
        return {
            username: data["rol"] 
            for username, data in self._usuarios_db.items()
            if data.get("activo", False)
        }
    
    def crear_usuario_temporal(self, username: str, password: str, rol: Rol, codigo_anonimo: Optional[str] = None) -> bool:
        """
        Crea un usuario temporal para testing.
        
        SOLO PARA DESARROLLO - NO usar en producción.
        
        Args:
            username: Nombre de usuario
            password: Contraseña en texto plano
            rol: Rol del usuario
            codigo_anonimo: Código anónimo si es estudiante
            
        Returns:
            True si el usuario fue creado
        """
        if os.getenv("DEBUG", "False").lower() != "true":
            return False
        
        if username in self._usuarios_db:
            return False  # Usuario ya existe
        
        # Generar ID único
        max_id = max([data["usuario_id"] for data in self._usuarios_db.values()], default=0)
        
        self._usuarios_db[username] = {
            "usuario_id": max_id + 1,
            "password_hash": hash_password(password),
            "rol": rol.value,
            "codigo_anonimo": codigo_anonimo,
            "activo": True,
            "fecha_creacion": datetime.utcnow().isoformat()
        }
        
        return True


# Instancia global del servicio (singleton para datos simulados)
auth_service = AuthService()


# Funciones de conveniencia para usar en endpoints
async def authenticate_user_login(credenciales: CredencialesLogin) -> TokenResponse:
    """
    Función de conveniencia para login de usuarios.
    
    Args:
        credenciales: Credenciales de login
        
    Returns:
        TokenResponse con token JWT
    """
    return await auth_service.login(credenciales)


async def verify_user_token(token: str) -> UsuarioAutenticado:
    """
    Función de conveniencia para verificar tokens.
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        UsuarioAutenticado si el token es válido
    """
    return await auth_service.verificar_token(token)


async def logout_user(token: str) -> bool:
    """
    Función de conveniencia para logout de usuarios.
    
    Args:
        token: Token JWT a invalidar
        
    Returns:
        True si el logout fue exitoso
    """
    return await auth_service.logout(token)