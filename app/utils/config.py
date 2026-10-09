"""
Configuración de la aplicación
Manejo centralizado de variables de entorno conforme a requisitos 10.2 y 11.1
"""

import os
from typing import Optional


class Config:
    """Configuración de la aplicación basada en variables de entorno"""
    
    # Gemini API (Requisito 10.2)
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Database Configuration
    DATABASE_URL: str = os.getenv("DATABASE_URL", "asistente_cni.db")
    
    # JWT Configuration
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_EXPIRATION_HOURS: int = int(os.getenv("JWT_EXPIRATION_HOURS", "8"))
    
    # Application Configuration
    APP_NAME: str = os.getenv("APP_NAME", "Asistente de Retroalimentación CNI")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    
    # Server Configuration
    HOST: str = os.getenv("HOST", "127.0.0.1")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # MCP Server Configuration (Week 4 Integration)
    MCP_SERVER_URL: str = os.getenv("MCP_SERVER_URL", "http://localhost:3001")
    MCP_SERVER_TIMEOUT: int = int(os.getenv("MCP_SERVER_TIMEOUT", "10"))
    
    # CORS Configuration
    CORS_ORIGINS: list[str] = os.getenv("CORS_ORIGINS", "http://localhost:8000").split(",")
    
    @classmethod
    def validate_required_vars(cls) -> None:
        """
        Valida que todas las variables de entorno requeridas estén configuradas
        Requisito 10.2: La clave GEMINI_API_KEY debe estar en variables de entorno
        """
        required_vars = {
            "GEMINI_API_KEY": cls.GEMINI_API_KEY,
            "JWT_SECRET_KEY": cls.JWT_SECRET_KEY
        }
        
        missing_vars = [var for var, value in required_vars.items() if not value]
        if missing_vars:
            raise ValueError(
                f"Variables de entorno requeridas no configuradas: {missing_vars}. "
                f"Consulte el archivo .env.example para más información."
            )
    
    @classmethod
    def is_development(cls) -> bool:
        """Retorna True si la aplicación está en modo desarrollo"""
        return cls.DEBUG


# Instancia global de configuración
config = Config()


def get_config() -> Config:
    """
    Obtiene la configuración de la aplicación
    Valida las variables requeridas al acceder por primera vez
    """
    config.validate_required_vars()
    return config