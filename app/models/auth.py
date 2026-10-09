"""
Modelos de autenticación y control de acceso para el sistema CNI.

Este módulo define los modelos Pydantic relacionados con la autenticación,
autorización y manejo de sesiones de usuarios.
"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, validator
from .enums import Rol, CodigoAnonimo


class TokenResponse(BaseModel):
    """
    Respuesta del sistema de autenticación con token JWT.
    
    Valida: Requisitos 1.1, 1.3
    """
    access_token: str = Field(
        ..., 
        description="Token JWT para autenticación de sesiones",
        min_length=20
    )
    token_type: str = Field(
        default="bearer",
        description="Tipo de token (siempre 'bearer')"
    )
    expires_in: int = Field(
        default=28800,  # 8 horas en segundos
        description="Tiempo de vida del token en segundos",
        ge=1
    )
    rol: Rol = Field(
        ...,
        description="Rol del usuario autenticado"
    )


class UsuarioAutenticado(BaseModel):
    """
    Información del usuario autenticado extraída del token JWT.
    
    Valida: Requisitos 1.1, 1.4, 11.5
    """
    usuario_id: int = Field(
        ...,
        description="Identificador único del usuario",
        ge=1
    )
    nombre_usuario: str = Field(
        ...,
        description="Nombre de usuario para autenticación",
        min_length=1,
        max_length=80
    )
    rol: Rol = Field(
        ...,
        description="Rol activo del usuario"
    )
    codigo_anonimo: Optional[CodigoAnonimo] = Field(
        None,
        description="Código anónimo para estudiantes (Ley N.º 29733)",
        max_length=40
    )
    activo: bool = Field(
        default=True,
        description="Estado activo del usuario"
    )
    fecha_creacion: datetime = Field(
        ...,
        description="Fecha de creación de la cuenta"
    )

    @validator('codigo_anonimo', always=True)
    def validar_codigo_anonimo(cls, v, values):
        """
        Valida que estudiantes tengan código anónimo y otros roles no.
        
        Valida: Requisito 11.5
        """
        rol = values.get('rol')
        if rol == Rol.ESTUDIANTE and not v:
            raise ValueError("Estudiantes deben tener código anónimo")
        if rol != Rol.ESTUDIANTE and v:
            raise ValueError("Solo estudiantes pueden tener código anónimo")
        return v


class CredencialesLogin(BaseModel):
    """
    Credenciales enviadas por el usuario para autenticación.
    
    Valida: Requisitos 1.1, 1.2
    """
    nombre_usuario: str = Field(
        ...,
        description="Nombre de usuario",
        min_length=1,
        max_length=80,
        strip_whitespace=True
    )
    contrasena: str = Field(
        ...,
        description="Contraseña del usuario",
        min_length=1,
        max_length=255
    )

    @validator('nombre_usuario')
    def validar_nombre_usuario(cls, v):
        """Valida que el nombre de usuario no esté vacío después de strip."""
        if not v or v.isspace():
            raise ValueError("Nombre de usuario no puede estar vacío")
        return v

    @validator('contrasena')
    def validar_contrasena(cls, v):
        """Valida que la contraseña no esté vacía."""
        if not v:
            raise ValueError("Contraseña no puede estar vacía")
        return v


class RegistroAcceso(BaseModel):
    """
    Modelo para registros de auditoría del sistema.
    
    Valida: Requisitos 11.3, 11.4
    """
    registro_acceso_id: Optional[int] = Field(
        None,
        description="ID del registro (auto-generado)",
        ge=1
    )
    usuario_id: Optional[int] = Field(
        None,
        description="ID del usuario que realizó la acción",
        ge=1
    )
    rol_activo: Optional[Rol] = Field(
        None,
        description="Rol activo durante la acción"
    )
    tipo_evento: str = Field(
        ...,
        description="Tipo de evento registrado",
        max_length=50
    )
    tipo_consulta: str = Field(
        ...,
        description="Descripción del tipo de consulta",
        max_length=80
    )
    codigo_resultado: Optional[int] = Field(
        None,
        description="Código de resultado de la operación",
        ge=0,
        le=999
    )
    fecha_hora: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp del evento"
    )


# Excepciones personalizadas para autenticación
class AuthError(Exception):
    """Error base de autenticación."""
    pass


class TokenExpiradoError(AuthError):
    """Token JWT expirado o inválido."""
    pass


class CredencialesInvalidasError(AuthError):
    """Credenciales de usuario incorrectas."""
    pass


class AccesoNoAutorizadoError(AuthError):
    """Usuario no autorizado para acceder al recurso."""
    pass