"""
Utilidades de autenticación JWT para el sistema CNI.

Este módulo implementa las funciones principales para el manejo de tokens JWT:
- Crear tokens JWT con expiración
- Verificar y decodificar tokens
- Verificar credenciales de usuarios
- Control de acceso por rol

Valida: Requisitos 1.1, 1.2, 1.3, 1.4
"""

import os
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
import bcrypt
from jose import jwt, JWTError
from pydantic import ValidationError

from app.models.auth import (
    UsuarioAutenticado, CredencialesLogin, TokenResponse,
    TokenExpiradoError, CredencialesInvalidasError, AccesoNoAutorizadoError
)
from app.models.enums import Rol


# Configuración JWT desde variables de entorno
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
JWT_ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
JWT_EXPIRE_HOURS = int(os.getenv("JWT_EXPIRE_HOURS", "8"))

if not JWT_SECRET_KEY:
    raise ValueError("JWT_SECRET_KEY no está configurado en las variables de entorno")

if len(JWT_SECRET_KEY) < 32:
    raise ValueError("JWT_SECRET_KEY debe tener al menos 32 caracteres")


def crear_token_jwt(usuario: UsuarioAutenticado) -> TokenResponse:
    """
    Crea un token JWT para un usuario autenticado.
    
    Args:
        usuario: Usuario autenticado del que generar el token
        
    Returns:
        TokenResponse con el token JWT y metadatos
        
    Raises:
        ValueError: Si los datos del usuario son inválidos
        
    Valida: Requisitos 1.1, 1.3
    """
    if not usuario.activo:
        raise ValueError("No se puede crear token para usuario inactivo")
    
    # Calcular tiempo de expiración
    now = datetime.utcnow()
    expire_at = now + timedelta(hours=JWT_EXPIRE_HOURS)
    
    # Payload del token JWT
    payload = {
        "sub": str(usuario.usuario_id),
        "username": usuario.nombre_usuario,
        "rol": usuario.rol.value,
        "codigo_anonimo": usuario.codigo_anonimo,
        "activo": usuario.activo,
        "iat": now,
        "exp": expire_at
    }
    
    # Crear el token
    token = jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)
    
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        expires_in=JWT_EXPIRE_HOURS * 3600,  # Convertir a segundos
        rol=usuario.rol
    )


def verificar_token_jwt(token: str) -> UsuarioAutenticado:
    """
    Verifica y decodifica un token JWT.
    
    Args:
        token: Token JWT a verificar
        
    Returns:
        UsuarioAutenticado con los datos del token
        
    Raises:
        TokenExpiradoError: Si el token ha expirado
        CredencialesInvalidasError: Si el token es inválido
        
    Valida: Requisitos 1.3, 1.4
    """
    try:
        # Decodificar el token
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        
        # Verificar campos obligatorios
        usuario_id = payload.get("sub")
        username = payload.get("username")
        rol_str = payload.get("rol")
        
        if not all([usuario_id, username, rol_str]):
            raise CredencialesInvalidasError("Token JWT contiene campos faltantes")
        
        # Convertir y validar rol
        try:
            rol = Rol(rol_str)
        except ValueError:
            raise CredencialesInvalidasError(f"Rol inválido en token: {rol_str}")
        
        # Extraer otros campos con valores por defecto
        codigo_anonimo = payload.get("codigo_anonimo")
        activo = payload.get("activo", True)
        iat_timestamp = payload.get("iat")
        
        # Convertir timestamp a datetime si está presente
        fecha_creacion = datetime.utcfromtimestamp(iat_timestamp) if iat_timestamp else datetime.utcnow()
        
        # Crear y retornar usuario autenticado
        return UsuarioAutenticado(
            usuario_id=int(usuario_id),
            nombre_usuario=username,
            rol=rol,
            codigo_anonimo=codigo_anonimo,
            activo=activo,
            fecha_creacion=fecha_creacion
        )
        
    except jwt.ExpiredSignatureError:
        raise TokenExpiradoError("El token JWT ha expirado")
    except (jwt.JWTClaimsError, jwt.InvalidTokenError, JWTError) as e:
        raise CredencialesInvalidasError(f"Token JWT inválido: {str(e)}")
    except (ValueError, ValidationError) as e:
        raise CredencialesInvalidasError(f"Datos inválidos en token: {str(e)}")


def autenticar_usuario(credenciales: CredencialesLogin, usuarios_db: Dict[str, Any]) -> Optional[UsuarioAutenticado]:
    """
    Autentica un usuario verificando sus credenciales contra la base de datos.
    
    Args:
        credenciales: Credenciales de login del usuario
        usuarios_db: Diccionario simulando la base de datos de usuarios
        
    Returns:
        UsuarioAutenticado si las credenciales son válidas, None en caso contrario
        
    Raises:
        CredencialesInvalidasError: Si las credenciales son inválidas
        
    Valida: Requisitos 1.1, 1.2
    """
    # Buscar usuario por nombre de usuario
    usuario_data = usuarios_db.get(credenciales.nombre_usuario)
    
    if not usuario_data:
        # Usuario no encontrado - mensaje genérico por seguridad
        raise CredencialesInvalidasError("Credenciales incorrectas")
    
    # Verificar contraseña usando bcrypt
    password_hash = usuario_data.get("password_hash", "")
    if not password_hash:
        raise CredencialesInvalidasError("Credenciales incorrectas")
    
    try:
        # Verificar la contraseña hasheada
        is_valid = bcrypt.checkpw(
            credenciales.contrasena.encode('utf-8'),
            password_hash.encode('utf-8')
        )
        
        if not is_valid:
            raise CredencialesInvalidasError("Credenciales incorrectas")
            
    except (ValueError, TypeError):
        raise CredencialesInvalidasError("Credenciales incorrectas")
    
    # Verificar que el usuario esté activo
    if not usuario_data.get("activo", False):
        raise CredencialesInvalidasError("Usuario inactivo")
    
    # Crear usuario autenticado
    try:
        rol = Rol(usuario_data["rol"])
    except (ValueError, KeyError):
        raise CredencialesInvalidasError("Datos de usuario corruptos")
    
    return UsuarioAutenticado(
        usuario_id=usuario_data["usuario_id"],
        nombre_usuario=credenciales.nombre_usuario,
        rol=rol,
        codigo_anonimo=usuario_data.get("codigo_anonimo"),
        activo=usuario_data["activo"],
        fecha_creacion=datetime.fromisoformat(usuario_data.get("fecha_creacion", datetime.utcnow().isoformat()))
    )


def verificar_acceso_rol(usuario: UsuarioAutenticado, rol_requerido: Rol, recurso: str = "") -> bool:
    """
    Verifica si un usuario tiene acceso a un recurso basado en su rol.
    
    Args:
        usuario: Usuario autenticado
        rol_requerido: Rol mínimo requerido para acceder al recurso
        recurso: Descripción del recurso (opcional, para logging)
        
    Returns:
        True si el usuario tiene acceso, False en caso contrario
        
    Raises:
        AccesoNoAutorizadoError: Si el acceso no está autorizado
        
    Valida: Requisitos 1.5, 1.6, 1.7
    """
    # Verificar que el usuario esté activo
    if not usuario.activo:
        raise AccesoNoAutorizadoError("Usuario inactivo")
    
    # Jerarquía de roles: DIRECCION > DOCENTE > ESTUDIANTE
    jerarquia_roles = {
        Rol.ESTUDIANTE: 1,
        Rol.DOCENTE: 2,
        Rol.DIRECCION: 3
    }
    
    nivel_usuario = jerarquia_roles.get(usuario.rol, 0)
    nivel_requerido = jerarquia_roles.get(rol_requerido, 0)
    
    # Verificar acceso jerárquico
    if nivel_usuario < nivel_requerido:
        mensaje = f"Rol {usuario.rol.value} no autorizado para acceder"
        if recurso:
            mensaje += f" a {recurso}"
        raise AccesoNoAutorizadoError(mensaje)
    
    return True


def verificar_acceso_estudiante_propio(usuario: UsuarioAutenticado, estudiante_id: int) -> bool:
    """
    Verifica que un estudiante solo acceda a sus propios datos.
    
    Args:
        usuario: Usuario autenticado
        estudiante_id: ID del estudiante al que se quiere acceder
        
    Returns:
        True si el acceso está autorizado
        
    Raises:
        AccesoNoAutorizadoError: Si un estudiante intenta acceder a datos de otro
        
    Valida: Requisito 1.5
    """
    if usuario.rol == Rol.ESTUDIANTE and usuario.usuario_id != estudiante_id:
        raise AccesoNoAutorizadoError("Los estudiantes solo pueden acceder a sus propios datos")
    
    return True


def verificar_acceso_docente_grupo(usuario: UsuarioAutenticado, estudiante_id: int, grupos_docente: list) -> bool:
    """
    Verifica que un docente solo acceda a estudiantes de sus grupos asignados.
    
    Args:
        usuario: Usuario autenticado (debe ser docente)
        estudiante_id: ID del estudiante
        grupos_docente: Lista de grupos asignados al docente
        
    Returns:
        True si el estudiante pertenece a los grupos del docente
        
    Raises:
        AccesoNoAutorizadoError: Si el estudiante no pertenece a los grupos del docente
        
    Valida: Requisito 1.6
    """
    if usuario.rol != Rol.DOCENTE:
        return True  # Solo aplicable a docentes
    
    # Esta función requiere consulta a la base de datos para verificar
    # que el estudiante_id pertenece a alguno de los grupos_docente
    # Por ahora, asumimos que grupos_docente contiene los IDs de estudiantes permitidos
    if estudiante_id not in grupos_docente:
        raise AccesoNoAutorizadoError("El estudiante no pertenece a sus grupos asignados")
    
    return True


def verificar_acceso_direccion_agregado(usuario: UsuarioAutenticado, acceso_individual: bool = False) -> bool:
    """
    Verifica que la dirección solo acceda a datos agregados, nunca individuales.
    
    Args:
        usuario: Usuario autenticado
        acceso_individual: Si se está intentando acceder a datos de un estudiante específico
        
    Returns:
        True si el acceso está autorizado
        
    Raises:
        AccesoNoAutorizadoError: Si la dirección intenta acceder a datos individuales
        
    Valida: Requisito 1.7
    """
    if usuario.rol == Rol.DIRECCION and acceso_individual:
        raise AccesoNoAutorizadoError("La dirección solo puede acceder a datos agregados")
    
    return True


def extraer_token_bearer(authorization: str) -> str:
    """
    Extrae el token de un header Authorization con formato Bearer.
    
    Args:
        authorization: Header Authorization completo
        
    Returns:
        Token JWT extraído
        
    Raises:
        CredencialesInvalidasError: Si el formato del header es incorrecto
        
    Valida: Requisito 1.3
    """
    if not authorization:
        raise CredencialesInvalidasError("Header Authorization faltante")
    
    try:
        scheme, token = authorization.split(" ", 1)
        if scheme.lower() != "bearer":
            raise CredencialesInvalidasError("Esquema de autenticación debe ser Bearer")
        
        if not token or token.isspace():
            raise CredencialesInvalidasError("Token JWT faltante")
            
        return token.strip()
        
    except ValueError:
        raise CredencialesInvalidasError("Formato inválido del header Authorization")


def hash_password(password: str) -> str:
    """
    Genera un hash bcrypt de una contraseña.
    
    Args:
        password: Contraseña en texto plano
        
    Returns:
        Hash bcrypt de la contraseña
        
    Nota: Función de utilidad para testing y inicialización de datos
    """
    salt = bcrypt.gensalt(rounds=12)  # 12 rounds es un buen balance seguridad/rendimiento
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')