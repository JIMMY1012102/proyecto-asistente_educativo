"""
Tests unitarios para las utilidades de autenticación JWT.

Valida: Requisitos 1.1, 1.2, 1.3, 1.4
"""

import pytest
from datetime import datetime, timedelta
from unittest.mock import patch
import bcrypt

from app.models.auth import (
    CredencialesLogin, UsuarioAutenticado, TokenResponse,
    CredencialesInvalidasError, TokenExpiradoError
)
from app.models.enums import Rol
from app.utils.auth import (
    crear_token_jwt, verificar_token_jwt, autenticar_usuario,
    verificar_acceso_rol, extraer_token_bearer, hash_password
)


class TestJWTUtils:
    """Tests para funciones de utilidad JWT."""
    
    def test_crear_token_jwt_exitoso(self):
        """Test crear token JWT para usuario válido."""
        usuario = UsuarioAutenticado(
            usuario_id=1,
            nombre_usuario="test_user",
            rol=Rol.ESTUDIANTE,
            codigo_anonimo="EST-001",
            activo=True,
            fecha_creacion=datetime.utcnow()
        )
        
        token_response = crear_token_jwt(usuario)
        
        assert isinstance(token_response, TokenResponse)
        assert token_response.token_type == "bearer"
        assert token_response.rol == Rol.ESTUDIANTE
        assert len(token_response.access_token) > 20
        assert token_response.expires_in == 28800  # 8 horas en segundos
    
    def test_crear_token_usuario_inactivo(self):
        """Test crear token para usuario inactivo debe fallar."""
        usuario = UsuarioAutenticado(
            usuario_id=1,
            nombre_usuario="inactive_user",
            rol=Rol.ESTUDIANTE,
            codigo_anonimo="EST-001",
            activo=False,
            fecha_creacion=datetime.utcnow()
        )
        
        with pytest.raises(ValueError, match="No se puede crear token para usuario inactivo"):
            crear_token_jwt(usuario)
    
    def test_verificar_token_jwt_valido(self):
        """Test verificar token JWT válido."""
        # Crear usuario y token
        usuario_original = UsuarioAutenticado(
            usuario_id=123,
            nombre_usuario="test_user",
            rol=Rol.DOCENTE,
            codigo_anonimo=None,
            activo=True,
            fecha_creacion=datetime.utcnow()
        )
        
        token_response = crear_token_jwt(usuario_original)
        
        # Verificar token
        usuario_verificado = verificar_token_jwt(token_response.access_token)
        
        assert usuario_verificado.usuario_id == 123
        assert usuario_verificado.nombre_usuario == "test_user"
        assert usuario_verificado.rol == Rol.DOCENTE
        assert usuario_verificado.activo is True
    
    def test_verificar_token_jwt_invalido(self):
        """Test verificar token JWT inválido."""
        token_invalido = "token.invalido.aqui"
        
        with pytest.raises(CredencialesInvalidasError, match="Token JWT inválido"):
            verificar_token_jwt(token_invalido)
    
    @patch('app.utils.auth.jwt.decode')
    def test_verificar_token_expirado(self, mock_decode):
        """Test verificar token JWT expirado."""
        from jose import jwt
        
        # Simular token expirado
        mock_decode.side_effect = jwt.ExpiredSignatureError("Token expired")
        
        with pytest.raises(TokenExpiradoError, match="El token JWT ha expirado"):
            verificar_token_jwt("token.expirado.aqui")
    
    def test_extraer_token_bearer_valido(self):
        """Test extraer token de header Authorization válido."""
        authorization = "Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
        
        token = extraer_token_bearer(authorization)
        
        assert token == "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
    
    def test_extraer_token_bearer_esquema_incorrecto(self):
        """Test extraer token con esquema incorrecto."""
        authorization = "Basic dXNlcjpwYXNzd29yZA=="
        
        with pytest.raises(CredencialesInvalidasError, match="Esquema de autenticación debe ser Bearer"):
            extraer_token_bearer(authorization)
    
    def test_extraer_token_bearer_formato_invalido(self):
        """Test extraer token con formato inválido."""
        authorization = "Bearer"
        
        with pytest.raises(CredencialesInvalidasError, match="Token JWT faltante"):
            extraer_token_bearer(authorization)
    
    def test_extraer_token_bearer_faltante(self):
        """Test extraer token sin header Authorization."""
        with pytest.raises(CredencialesInvalidasError, match="Header Authorization faltante"):
            extraer_token_bearer("")


class TestAuthenticacion:
    """Tests para autenticación de usuarios."""
    
    def test_autenticar_usuario_exitoso(self):
        """Test autenticación exitosa."""
        # Preparar datos simulados
        password = "test123"
        password_hash = hash_password(password)
        
        usuarios_db = {
            "test_user": {
                "usuario_id": 1,
                "password_hash": password_hash,
                "rol": Rol.ESTUDIANTE.value,
                "codigo_anonimo": "EST-001",
                "activo": True,
                "fecha_creacion": "2024-01-15T08:00:00"
            }
        }
        
        credenciales = CredencialesLogin(
            nombre_usuario="test_user",
            contrasena=password
        )
        
        usuario = autenticar_usuario(credenciales, usuarios_db)
        
        assert usuario is not None
        assert usuario.usuario_id == 1
        assert usuario.nombre_usuario == "test_user"
        assert usuario.rol == Rol.ESTUDIANTE
        assert usuario.codigo_anonimo == "EST-001"
    
    def test_autenticar_usuario_no_existe(self):
        """Test autenticación con usuario inexistente."""
        usuarios_db = {}
        
        credenciales = CredencialesLogin(
            nombre_usuario="inexistente",
            contrasena="password"
        )
        
        with pytest.raises(CredencialesInvalidasError, match="Credenciales incorrectas"):
            autenticar_usuario(credenciales, usuarios_db)
    
    def test_autenticar_usuario_contrasena_incorrecta(self):
        """Test autenticación con contraseña incorrecta."""
        password_hash = hash_password("password_correcta")
        
        usuarios_db = {
            "test_user": {
                "usuario_id": 1,
                "password_hash": password_hash,
                "rol": Rol.ESTUDIANTE.value,
                "codigo_anonimo": "EST-001",
                "activo": True,
                "fecha_creacion": "2024-01-15T08:00:00"
            }
        }
        
        credenciales = CredencialesLogin(
            nombre_usuario="test_user",
            contrasena="password_incorrecta"
        )
        
        with pytest.raises(CredencialesInvalidasError, match="Credenciales incorrectas"):
            autenticar_usuario(credenciales, usuarios_db)
    
    def test_autenticar_usuario_inactivo(self):
        """Test autenticación con usuario inactivo."""
        password = "test123"
        password_hash = hash_password(password)
        
        usuarios_db = {
            "test_user": {
                "usuario_id": 1,
                "password_hash": password_hash,
                "rol": Rol.ESTUDIANTE.value,
                "codigo_anonimo": "EST-001",
                "activo": False,
                "fecha_creacion": "2024-01-15T08:00:00"
            }
        }
        
        credenciales = CredencialesLogin(
            nombre_usuario="test_user",
            contrasena=password
        )
        
        with pytest.raises(CredencialesInvalidasError, match="Usuario inactivo"):
            autenticar_usuario(credenciales, usuarios_db)


class TestControlAcceso:
    """Tests para control de acceso por rol."""
    
    def test_verificar_acceso_rol_permitido(self):
        """Test acceso permitido con rol suficiente."""
        usuario = UsuarioAutenticado(
            usuario_id=1,
            nombre_usuario="docente",
            rol=Rol.DOCENTE,
            codigo_anonimo=None,
            activo=True,
            fecha_creacion=datetime.utcnow()
        )
        
        # Docente puede acceder a recursos de estudiante
        result = verificar_acceso_rol(usuario, Rol.ESTUDIANTE, "recurso test")
        assert result is True
    
    def test_verificar_acceso_rol_denegado(self):
        """Test acceso denegado con rol insuficiente."""
        usuario = UsuarioAutenticado(
            usuario_id=1,
            nombre_usuario="estudiante",
            rol=Rol.ESTUDIANTE,
            codigo_anonimo="EST-001",
            activo=True,
            fecha_creacion=datetime.utcnow()
        )
        
        # Estudiante no puede acceder a recursos de docente
        with pytest.raises(Exception, match="no autorizado"):
            verificar_acceso_rol(usuario, Rol.DOCENTE, "recurso administrativo")
    
    def test_verificar_acceso_usuario_inactivo(self):
        """Test acceso denegado para usuario inactivo."""
        usuario = UsuarioAutenticado(
            usuario_id=1,
            nombre_usuario="inactivo",
            rol=Rol.ESTUDIANTE,
            codigo_anonimo="EST-001",
            activo=False,
            fecha_creacion=datetime.utcnow()
        )
        
        with pytest.raises(Exception, match="Usuario inactivo"):
            verificar_acceso_rol(usuario, Rol.ESTUDIANTE)


class TestHashPassword:
    """Tests para hashing de contraseñas."""
    
    def test_hash_password_genera_hash_valido(self):
        """Test que hash_password genera hash bcrypt válido."""
        password = "mi_password_123"
        
        password_hash = hash_password(password)
        
        # Verificar que es un hash bcrypt válido
        assert password_hash.startswith("$2b$")
        assert len(password_hash) >= 60
    
    def test_hash_password_verificacion(self):
        """Test que el hash generado se puede verificar correctamente."""
        password = "test_password_456"
        
        password_hash = hash_password(password)
        
        # Verificar que la contraseña original coincide
        assert bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8'))
        
        # Verificar que contraseña incorrecta no coincide
        assert not bcrypt.checkpw("password_incorrecta".encode('utf-8'), password_hash.encode('utf-8'))
    
    def test_hash_password_diferentes_para_misma_password(self):
        """Test que diferentes llamadas generan hashes diferentes por el salt."""
        password = "mismo_password"
        
        hash1 = hash_password(password)
        hash2 = hash_password(password)
        
        # Los hashes deben ser diferentes debido al salt aleatorio
        assert hash1 != hash2
        
        # Pero ambos deben verificar correctamente
        assert bcrypt.checkpw(password.encode('utf-8'), hash1.encode('utf-8'))
        assert bcrypt.checkpw(password.encode('utf-8'), hash2.encode('utf-8'))