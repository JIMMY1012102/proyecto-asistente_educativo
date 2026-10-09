"""
Configuración de la aplicación.

Este módulo maneja la lectura de variables de entorno y configuración
del sistema siguiendo los requisitos 10.2 y 11.2 de seguridad y variables de entorno.
"""

import os
from enum import Enum
from pathlib import Path
from typing import List, Optional

from pydantic import BaseSettings, Field, validator


class Environment(str, Enum):
    """Tipos de entorno disponibles."""
    DEVELOPMENT = "development"
    TESTING = "testing"
    PRODUCTION = "production"


class BaseConfig(BaseSettings):
    """Configuración base compartida entre entornos."""
    
    # Environment
    environment: Environment = Field(default=Environment.DEVELOPMENT, env="ENVIRONMENT")
    
    # Gemini API Configuration (Requisito 10.2)
    gemini_api_key: str = Field(default="", env="GEMINI_API_KEY")
    gemini_timeout_seconds: int = Field(default=8, env="GEMINI_TIMEOUT_SECONDS")
    
    # JWT Configuration
    jwt_secret_key: str = Field(default="", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", env="JWT_ALGORITHM")
    jwt_expire_hours: int = Field(default=8, env="JWT_EXPIRE_HOURS")
    
    # Database Configuration
    database_path: str = Field(default="./data/asistente_cni.db", env="DATABASE_PATH")
    
    # MCP Server Configuration (Semana 4 - Requisito 11.2)
    mcp_server_host: str = Field(default="localhost", env="MCP_SERVER_HOST")
    mcp_server_port: int = Field(default=8080, env="MCP_SERVER_PORT")
    mcp_timeout_seconds: int = Field(default=10, env="MCP_TIMEOUT_SECONDS")
    mcp_read_only: bool = Field(default=True, env="MCP_READ_ONLY")
    
    # Logging Configuration (Requisito 11.3)
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file_path: str = Field(default="./logs/asistente_cni.log", env="LOG_FILE_PATH")
    log_max_size_mb: int = Field(default=10, env="LOG_MAX_SIZE_MB")
    log_backup_count: int = Field(default=5, env="LOG_BACKUP_COUNT")
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT"
    )
    
    # FastAPI Configuration
    app_name: str = Field(default="Asistente CNI", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug_mode: bool = Field(default=False, env="DEBUG_MODE")
    host: str = Field(default="127.0.0.1", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:8000,http://127.0.0.1:8000",
        env="CORS_ORIGINS"
    )
    cors_allow_credentials: bool = Field(default=True, env="CORS_ALLOW_CREDENTIALS")
    cors_allow_methods: str = Field(default="GET,POST,PUT,DELETE", env="CORS_ALLOW_METHODS")
    cors_allow_headers: str = Field(default="*", env="CORS_ALLOW_HEADERS")
    
    # Security Configuration
    session_timeout_hours: int = Field(default=8, env="SESSION_TIMEOUT_HOURS")
    max_login_attempts: int = Field(default=5, env="MAX_LOGIN_ATTEMPTS")
    
    @validator("jwt_secret_key")
    def validate_jwt_secret(cls, v: str, values: dict) -> str:
        """Valida que la clave JWT sea segura en producción."""
        env = values.get("environment", Environment.DEVELOPMENT)
        if env == Environment.PRODUCTION and (not v or len(v) < 32):
            raise ValueError("JWT_SECRET_KEY debe tener al menos 32 caracteres en producción")
        return v
    
    @validator("gemini_api_key")
    def validate_gemini_key(cls, v: str, values: dict) -> str:
        """Valida que la clave de Gemini esté configurada."""
        if not v:
            raise ValueError("GEMINI_API_KEY es requerida en variables de entorno")
        return v
    
    @property
    def cors_origins_list(self) -> List[str]:
        """Convierte la cadena de orígenes CORS a lista."""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    @property
    def cors_methods_list(self) -> List[str]:
        """Convierte la cadena de métodos CORS a lista."""
        return [method.strip() for method in self.cors_allow_methods.split(",")]
    
    @property
    def is_development(self) -> bool:
        """Verifica si estamos en entorno de desarrollo."""
        return self.environment == Environment.DEVELOPMENT
    
    @property
    def is_testing(self) -> bool:
        """Verifica si estamos en entorno de testing."""
        return self.environment == Environment.TESTING
    
    @property
    def is_production(self) -> bool:
        """Verifica si estamos en entorno de producción."""
        return self.environment == Environment.PRODUCTION
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True


class DevelopmentConfig(BaseConfig):
    """Configuración para entorno de desarrollo."""
    
    debug_mode: bool = True
    log_level: str = "DEBUG"
    jwt_secret_key: str = "dev_secret_key_not_for_production_32chars"
    
    # Permitir orígenes más permisivos en desarrollo
    cors_origins: str = "http://localhost:3000,http://localhost:8000,http://127.0.0.1:8000"


class TestingConfig(BaseConfig):
    """Configuración para entorno de testing."""
    
    environment: Environment = Environment.TESTING
    database_path: str = ":memory:"  # Base de datos en memoria para tests
    log_level: str = "WARNING"
    jwt_secret_key: str = "test_secret_key_for_testing_32chars"
    gemini_api_key: str = "test_key"  # Mock para testing
    mcp_server_host: str = "localhost"
    mcp_server_port: int = 9999  # Puerto diferente para testing
    
    # Configuración más restrictiva para tests
    cors_origins: str = "http://localhost:3000"


class ProductionConfig(BaseConfig):
    """Configuración para entorno de producción."""
    
    environment: Environment = Environment.PRODUCTION
    debug_mode: bool = False
    log_level: str = "INFO"
    
    # En producción, estas configuraciones DEBEN venir de variables de entorno
    jwt_secret_key: str = Field(env="JWT_SECRET_KEY")
    gemini_api_key: str = Field(env="GEMINI_API_KEY")
    
    # Configuración más estricta de CORS
    cors_origins: str = Field(env="CORS_ORIGINS")


def get_settings() -> BaseConfig:
    """
    Factory function para obtener la configuración según el entorno.
    
    Returns:
        BaseConfig: Instancia de configuración apropiada para el entorno.
    """
    env = os.getenv("ENVIRONMENT", Environment.DEVELOPMENT)
    
    if env == Environment.TESTING:
        return TestingConfig()
    elif env == Environment.PRODUCTION:
        return ProductionConfig()
    else:
        return DevelopmentConfig()


# Instancia global de configuración
settings = get_settings()


def validate_configuration() -> None:
    """
    Valida la configuración requerida según los requisitos.
    
    Raises:
        ValueError: Si faltan configuraciones críticas.
        FileNotFoundError: Si no se pueden crear directorios necesarios.
    """
    # Validar configuraciones críticas (Requisito 10.2)
    if not settings.gemini_api_key:
        raise ValueError(
            "GEMINI_API_KEY es requerida. "
            "Por favor configúrela en el archivo .env o variables de entorno"
        )
    
    if settings.is_production and settings.jwt_secret_key == "dev_secret_key_not_for_production_32chars":
        raise ValueError(
            "JWT_SECRET_KEY de producción es requerida. "
            "No use la clave de desarrollo en producción"
        )
    
    # Validar configuración del servidor MCP (Requisito 11.2)
    if not settings.mcp_read_only:
        raise ValueError(
            "El servidor MCP debe estar configurado en modo solo lectura (MCP_READ_ONLY=true)"
        )
    
    # Crear directorios necesarios
    try:
        if settings.database_path != ":memory:":
            Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)
        Path(settings.log_file_path).parent.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise FileNotFoundError(f"No se pudieron crear directorios necesarios: {e}")


def get_database_url() -> str:
    """
    Obtiene la URL de conexión a la base de datos.
    
    Returns:
        str: URL de conexión SQLite.
    """
    return f"sqlite:///{settings.database_path}"


def get_mcp_server_url() -> str:
    """
    Obtiene la URL del servidor MCP.
    
    Returns:
        str: URL completa del servidor MCP.
    """
    return f"http://{settings.mcp_server_host}:{settings.mcp_server_port}"