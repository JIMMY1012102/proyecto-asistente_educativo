"""
Tests de integración para el sistema de autenticación completo.

Valida: Requisitos 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7
"""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch
import os

# Configurar variables de entorno para testing
os.environ["JWT_SECRET_KEY"] = "test_secret_key_for_jwt_at_least_32_characters_long_12345"
os.environ["GEMINI_API_KEY"] = "test_gemini_api_key"
os.environ["DEBUG"] = "True"

from main import app
from app.models.enums import Rol


class TestAuthIntegration:
    """Tests de integración para autenticación completa."""
    
    def setup_method(self):
        """Configurar cliente de test."""
        self.client = TestClient(app)
    
    def test_login_estudiante_exitoso(self):
        """Test login exitoso para estudiante."""
        response = self.client.post("/auth/login", json={
            "nombre_usuario": "estudiante01",
            "contrasena": "password123"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["rol"] == Rol.ESTUDIANTE.value
        assert data["expires_in"] == 28800
    
    def test_login_docente_exitoso(self):
        """Test login exitoso para docente."""
        response = self.client.post("/auth/login", json={
            "nombre_usuario": "docente01",
            "contrasena": "docente123"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["rol"] == Rol.DOCENTE.value
    
    def test_login_direccion_exitoso(self):
        """Test login exitoso para dirección."""
        response = self.client.post("/auth/login", json={
            "nombre_usuario": "direccion",
            "contrasena": "direccion123"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert data["rol"] == Rol.DIRECCION.value
    
    def test_login_credenciales_invalidas(self):
        """Test login con credenciales inválidas."""
        response = self.client.post("/auth/login", json={
            "nombre_usuario": "usuario_inexistente",
            "contrasena": "password_incorrecta"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Credenciales incorrectas"
    
    def test_login_contrasena_incorrecta(self):
        """Test login con contraseña incorrecta."""
        response = self.client.post("/auth/login", json={
            "nombre_usuario": "estudiante01",
            "contrasena": "password_incorrecta"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert data["detail"] == "Credenciales incorrectas"
    
    def test_get_user_info_con_token_valido(self):
        """Test obtener info de usuario con token válido."""
        # Primero hacer login
        login_response = self.client.post("/auth/login", json={
            "nombre_usuario": "estudiante01",
            "contrasena": "password123"
        })
        
        token = login_response.json()["access_token"]
        
        # Luego obtener info del usuario
        response = self.client.get("/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["nombre_usuario"] == "estudiante01"
        assert data["rol"] == Rol.ESTUDIANTE.value
        assert data["codigo_anonimo"] == "EST-2024-001"
        assert data["activo"] is True
    
    def test_get_user_info_sin_token(self):
        """Test obtener info de usuario sin token."""
        response = self.client.get("/auth/me")
        
        assert response.status_code == 401
        data = response.json()
        assert "Header Authorization faltante" in data["message"]
    
    def test_get_user_info_token_invalido(self):
        """Test obtener info de usuario con token inválido."""
        response = self.client.get("/auth/me", headers={
            "Authorization": "Bearer token_invalido_aqui"
        })
        
        assert response.status_code == 401
        data = response.json()
        assert "Token inválido" in data["message"]
    
    def test_verify_token_valido(self):
        """Test verificar token válido."""
        # Login y obtener token
        login_response = self.client.post("/auth/login", json={
            "nombre_usuario": "docente01",
            "contrasena": "docente123"
        })
        
        token = login_response.json()["access_token"]
        
        # Verificar token
        response = self.client.get("/auth/verify", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["valid"] is True
        assert data["rol"] == Rol.DOCENTE.value
    
    def test_logout_exitoso(self):
        """Test logout exitoso."""
        # Login y obtener token
        login_response = self.client.post("/auth/login", json={
            "nombre_usuario": "direccion",
            "contrasena": "direccion123"
        })
        
        token = login_response.json()["access_token"]
        
        # Logout
        response = self.client.post("/auth/logout", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert response.status_code == 200
        data = response.json()
        
        assert "Logout exitoso" in data["message"]
        assert data["success"] is True
    
    def test_acceso_endpoint_protegido_sin_auth(self):
        """Test acceso a endpoint protegido sin autenticación."""
        # Intentar acceder a endpoint protegido sin token
        response = self.client.get("/auth/me")
        
        assert response.status_code == 401
    
    def test_get_test_usuarios_en_debug(self):
        """Test obtener usuarios de test en modo DEBUG."""
        response = self.client.get("/auth/test/usuarios")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "usuarios_disponibles" in data
        usuarios = data["usuarios_disponibles"]
        
        # Verificar que hay usuarios de cada rol
        roles_disponibles = list(usuarios.values())
        assert Rol.ESTUDIANTE.value in roles_disponibles
        assert Rol.DOCENTE.value in roles_disponibles
        assert Rol.DIRECCION.value in roles_disponibles
    
    def test_middleware_excluye_paths_publicos(self):
        """Test que middleware excluye paths públicos correctamente."""
        # Estos endpoints deben funcionar sin autenticación
        endpoints_publicos = ["/", "/health", "/auth/login"]
        
        for endpoint in endpoints_publicos:
            response = self.client.get(endpoint)
            # No debe ser 401 (no autorizado)
            assert response.status_code != 401
    
    def test_flujo_completo_autenticacion(self):
        """Test flujo completo de autenticación."""
        # 1. Login
        login_response = self.client.post("/auth/login", json={
            "nombre_usuario": "estudiante02",
            "contrasena": "password123"
        })
        
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]
        
        # 2. Verificar token
        verify_response = self.client.get("/auth/verify", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert verify_response.status_code == 200
        assert verify_response.json()["valid"] is True
        
        # 3. Obtener info del usuario
        me_response = self.client.get("/auth/me", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["nombre_usuario"] == "estudiante02"
        assert user_data["codigo_anonimo"] == "EST-2024-002"
        
        # 4. Logout
        logout_response = self.client.post("/auth/logout", headers={
            "Authorization": f"Bearer {token}"
        })
        
        assert logout_response.status_code == 200
        assert logout_response.json()["success"] is True


class TestValidacionDatos:
    """Tests para validación de datos de entrada."""
    
    def setup_method(self):
        """Configurar cliente de test."""
        self.client = TestClient(app)
    
    def test_login_datos_faltantes(self):
        """Test login con datos faltantes."""
        # Sin nombre de usuario
        response = self.client.post("/auth/login", json={
            "contrasena": "password123"
        })
        
        assert response.status_code == 422  # Validation Error
    
    def test_login_campos_vacios(self):
        """Test login con campos vacíos."""
        response = self.client.post("/auth/login", json={
            "nombre_usuario": "",
            "contrasena": ""
        })
        
        assert response.status_code == 422  # Validation Error
    
    def test_login_nombre_usuario_solo_espacios(self):
        """Test login con nombre de usuario solo espacios."""
        response = self.client.post("/auth/login", json={
            "nombre_usuario": "   ",
            "contrasena": "password123"
        })
        
        assert response.status_code == 422  # Validation Error


class TestSeguridad:
    """Tests de seguridad para autenticación."""
    
    def setup_method(self):
        """Configurar cliente de test."""
        self.client = TestClient(app)
    
    def test_token_no_expone_password(self):
        """Test que el token JWT no expone contraseñas."""
        # Login y obtener token
        login_response = self.client.post("/auth/login", json={
            "nombre_usuario": "estudiante01",
            "contrasena": "password123"
        })
        
        token = login_response.json()["access_token"]
        
        # Verificar que la contraseña no está en el token
        assert "password" not in token.lower()
        assert "contrasena" not in token.lower()
        assert "password123" not in token
    
    def test_error_credenciales_no_revela_detalles(self):
        """Test que errores de credenciales no revelan detalles específicos."""
        # Usuario inexistente
        response1 = self.client.post("/auth/login", json={
            "nombre_usuario": "usuario_inexistente",
            "contrasena": "cualquier_password"
        })
        
        # Usuario existente pero contraseña incorrecta
        response2 = self.client.post("/auth/login", json={
            "nombre_usuario": "estudiante01",
            "contrasena": "password_incorrecta"
        })
        
        # Ambos deben retornar el mismo mensaje genérico
        assert response1.status_code == 401
        assert response2.status_code == 401
        assert response1.json()["detail"] == response2.json()["detail"]
        assert response1.json()["detail"] == "Credenciales incorrectas"