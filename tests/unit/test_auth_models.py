# tests/unit/test_auth_models.py
"""
Pruebas unitarias para los modelos de autenticación.

Valida la correcta implementación de:
- Modelos Pydantic de usuario y autenticación
- Validadores de datos
- Excepciones personalizadas
"""
import pytest
from datetime import datetime, timedelta
from pydantic import ValidationError

from app.models.auth import (
    UserRole,
    User,
    UserCreate,
    UserInDB,
    LoginCredentials,
    Token,
    TokenData,
    UsuarioAutenticado,
    CredencialesInvalidasError,
    TokenExpiradoError,
    AccesoNoAutorizadoError,
    TokenInvalidoError,
)


class TestUserRole:
    """Pruebas para el enum UserRole."""
    
    def test_roles_validos(self):
        """Verifica que los roles definidos son correctos."""
        assert UserRole.ESTUDIANTE == "estudiante"
        assert UserRole.DOCENTE == "docente"
        assert UserRole.DIRECCION == "direccion"


class TestUserCreate:
    """Pruebas para el modelo UserCreate."""
    
    def test_crear_estudiante_valido(self):
        """Debe crear un estudiante con código anónimo."""
        user_data = {
            "nombre_usuario": "estudiante01",
            "contrasena": "password123",
            "rol": UserRole.ESTUDIANTE,
            "codigo_anonimo": "EST_2024_001",
            "activo": True
        }
        
        user = UserCreate(**user_data)
        
        assert user.nombre_usuario == "estudiante01"
        assert user.rol == UserRole.ESTUDIANTE
        assert user.codigo_anonimo == "EST_2024_001"
        assert user.activo is True
    
    def test_crear_docente_valido(self):
        """Debe crear un docente sin código anónimo."""
        user_data = {
            "nombre_usuario": "docente01", 
            "contrasena": "password456",
            "rol": UserRole.DOCENTE,
            "activo": True
        }
        
        user = UserCreate(**user_data)
        
        assert user.nombre_usuario == "docente01"
        assert user.rol == UserRole.DOCENTE
        assert user.codigo_anonimo is None
        assert user.activo is True
    
    def test_crear_direccion_valida(self):
        """Debe crear usuario de dirección sin código anónimo."""
        user_data = {
            "nombre_usuario": "direccion01",
            "contrasena": "password789", 
            "rol": UserRole.DIRECCION,
            "activo": True
        }
        
        user = UserCreate(**user_data)
        
        assert user.nombre_usuario == "direccion01"
        assert user.rol == UserRole.DIRECCION
        assert user.codigo_anonimo is None
    
    def test_estudiante_sin_codigo_anonimo_falla(self):
        """Debe fallar al crear estudiante sin código anónimo."""
        user_data = {
            "nombre_usuario": "estudiante02",
            "contrasena": "password123",
            "rol": UserRole.ESTUDIANTE,
            "activo": True
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "Los estudiantes deben tener un código anónimo" in str(exc_info.value)
    
    def test_docente_con_codigo_anonimo_falla(self):
        """Debe fallar al crear docente con código anónimo.""" 
        user_data = {
            "nombre_usuario": "docente02",
            "contrasena": "password456", 
            "rol": UserRole.DOCENTE,
            "codigo_anonimo": "DOC_001",
            "activo": True
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        assert "Solo los estudiantes pueden tener código anónimo" in str(exc_info.value)
    
    def test_validacion_nombre_usuario_corto(self):
        """Debe fallar con nombre de usuario muy corto."""
        user_data = {
            "nombre_usuario": "ab",  # Menos de 3 caracteres
            "contrasena": "password123",
            "rol": UserRole.ESTUDIANTE,
            "codigo_anonimo": "EST_001"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        errors = exc_info.value.errors()
        assert any("at least 3 characters" in str(error) for error in errors)
    
    def test_validacion_contrasena_corta(self):
        """Debe fallar con contraseña muy corta."""
        user_data = {
            "nombre_usuario": "estudiante03",
            "contrasena": "123",  # Menos de 6 caracteres
            "rol": UserRole.ESTUDIANTE,
            "codigo_anonimo": "EST_003"
        }
        
        with pytest.raises(ValidationError) as exc_info:
            UserCreate(**user_data)
        
        errors = exc_info.value.errors()
        assert any("at least 6 characters" in str(error) for error in errors)


class TestLoginCredentials:
    """Pruebas para el modelo LoginCredentials."""
    
    def test_credenciales_validas(self):
        """Debe crear credenciales válidas."""
        creds = LoginCredentials(
            nombre_usuario="usuario_test",
            contrasena="password123"
        )
        
        assert creds.nombre_usuario == "usuario_test"
        assert creds.contrasena == "password123"
    
    def test_credenciales_vacias_fallan(self):
        """Debe fallar con campos vacíos."""
        with pytest.raises(ValidationError):
            LoginCredentials(nombre_usuario="", contrasena="password")
        
        with pytest.raises(ValidationError):
            LoginCredentials(nombre_usuario="usuario", contrasena="")


class TestTokenData:
    """Pruebas para el modelo TokenData."""
    
    def test_token_data_valido(self):
        """Debe crear TokenData válido."""
        exp_time = datetime.utcnow() + timedelta(hours=8)
        
        token_data = TokenData(
            usuario_id=1,
            nombre_usuario="test_user",
            rol=UserRole.ESTUDIANTE,
            exp=exp_time
        )
        
        assert token_data.usuario_id == 1
        assert token_data.nombre_usuario == "test_user"
        assert token_data.rol == UserRole.ESTUDIANTE
        assert token_data.exp == exp_time


class TestUsuarioAutenticado:
    """Pruebas para el modelo UsuarioAutenticado."""
    
    def test_usuario_estudiante(self):
        """Debe identificar correctamente usuario estudiante."""
        usuario = UsuarioAutenticado(
            usuario_id=1,
            nombre_usuario="estudiante_test",
            rol=UserRole.ESTUDIANTE,
            codigo_anonimo="EST_001"
        )
        
        assert usuario.es_estudiante() is True
        assert usuario.es_docente() is False
        assert usuario.es_direccion() is False
    
    def test_usuario_docente(self):
        """Debe identificar correctamente usuario docente."""
        usuario = UsuarioAutenticado(
            usuario_id=2,
            nombre_usuario="docente_test",
            rol=UserRole.DOCENTE
        )
        
        assert usuario.es_estudiante() is False
        assert usuario.es_docente() is True
        assert usuario.es_direccion() is False
    
    def test_usuario_direccion(self):
        """Debe identificar correctamente usuario de dirección."""
        usuario = UsuarioAutenticado(
            usuario_id=3,
            nombre_usuario="direccion_test",
            rol=UserRole.DIRECCION
        )
        
        assert usuario.es_estudiante() is False
        assert usuario.es_docente() is False
        assert usuario.es_direccion() is True


class TestExcepcionesAuth:
    """Pruebas para las excepciones de autenticación."""
    
    def test_credenciales_invalidas_error(self):
        """Debe crear excepción de credenciales inválidas."""
        error = CredencialesInvalidasError()
        assert error.mensaje == "Credenciales incorrectas"
        
        error_custom = CredencialesInvalidasError("Usuario no encontrado")
        assert error_custom.mensaje == "Usuario no encontrado"
    
    def test_token_expirado_error(self):
        """Debe crear excepción de token expirado."""
        error = TokenExpiradoError()
        assert error.mensaje == "La sesión ha expirado"
    
    def test_acceso_no_autorizado_error(self):
        """Debe crear excepción de acceso no autorizado."""
        error = AccesoNoAutorizadoError()
        assert error.mensaje == "Acceso no autorizado"
    
    def test_token_invalido_error(self):
        """Debe crear excepción de token inválido."""
        error = TokenInvalidoError()
        assert error.mensaje == "Token inválido"