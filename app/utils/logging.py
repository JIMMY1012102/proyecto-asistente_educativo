"""
Sistema de logging estructurado para auditoría.

Este módulo implementa el sistema de logging requerido por los requisitos
11.3 y 11.4 para auditoría y cumplimiento de la Ley N.º 29733.
"""

import json
import logging
import logging.handlers
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from app.config import settings


class StructuredFormatter(logging.Formatter):
    """
    Formateador que produce logs estructurados en formato JSON.
    
    Incluye campos específicos para auditoría según requisitos de la aplicación.
    """
    
    def format(self, record: logging.LogRecord) -> str:
        """
        Formatea el registro de log como JSON estructurado.
        
        Args:
            record: Registro de log a formatear.
            
        Returns:
            str: Log formateado como JSON.
        """
        # Información básica del log
        log_data = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        
        # Añadir información adicional si está disponible
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, "user_role"):
            log_data["user_role"] = record.user_role
        
        if hasattr(record, "operation_type"):
            log_data["operation_type"] = record.operation_type
        
        if hasattr(record, "resource_accessed"):
            log_data["resource_accessed"] = record.resource_accessed
        
        if hasattr(record, "ip_address"):
            log_data["ip_address"] = record.ip_address
        
        if hasattr(record, "session_id"):
            log_data["session_id"] = record.session_id
        
        # Información de error si existe
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        return json.dumps(log_data, ensure_ascii=False)


def setup_logging() -> logging.Logger:
    """
    Configura el sistema de logging según los requisitos de auditoría.
    
    Returns:
        logging.Logger: Logger principal configurado.
    """
    # Crear directorio de logs si no existe
    log_path = Path(settings.log_file_path)
    log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configurar el logger principal
    logger = logging.getLogger("asistente_cni")
    logger.setLevel(getattr(logging, settings.log_level.upper()))
    
    # Evitar duplicar handlers si ya están configurados
    if logger.handlers:
        return logger
    
    # Handler para archivo con rotación
    file_handler = logging.handlers.RotatingFileHandler(
        filename=settings.log_file_path,
        maxBytes=settings.log_max_size_mb * 1024 * 1024,  # Convertir MB a bytes
        backupCount=settings.log_backup_count,
        encoding="utf-8"
    )
    
    # Handler para consola (solo en desarrollo)
    console_handler = logging.StreamHandler()
    
    # Aplicar formateadores
    structured_formatter = StructuredFormatter()
    file_handler.setFormatter(structured_formatter)
    
    if settings.is_development:
        # En desarrollo, usar formato legible en consola
        console_formatter = logging.Formatter(
            settings.log_format,
            datefmt="%Y-%m-%d %H:%M:%S"
        )
        console_handler.setFormatter(console_formatter)
        logger.addHandler(console_handler)
    
    logger.addHandler(file_handler)
    
    # Configurar loggers de terceros
    configure_third_party_loggers()
    
    return logger


def configure_third_party_loggers() -> None:
    """Configura el nivel de logging para librerías de terceros."""
    # Reducir verbosidad de loggers de terceros
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("fastapi").setLevel(logging.INFO)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    
    # En desarrollo, permitir más logs de uvicorn
    if settings.is_development:
        logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    else:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)


def log_audit_event(
    logger: logging.Logger,
    user_id: Optional[str],
    user_role: Optional[str],
    operation_type: str,
    message: str,
    resource_accessed: Optional[str] = None,
    ip_address: Optional[str] = None,
    session_id: Optional[str] = None,
    level: int = logging.INFO,
    **additional_data: Any
) -> None:
    """
    Registra un evento de auditoría con información estructurada.
    
    Args:
        logger: Logger a usar.
        user_id: ID del usuario (anonimizado según requisito 11.5).
        user_role: Rol del usuario.
        operation_type: Tipo de operación realizada.
        message: Mensaje descriptivo del evento.
        resource_accessed: Recurso al que se accedió (opcional).
        ip_address: Dirección IP del usuario (opcional).
        session_id: ID de la sesión (opcional).
        level: Nivel de logging.
        **additional_data: Datos adicionales para el log.
    """
    # Crear un LogRecord personalizado con información de auditoría
    record = logger.makeRecord(
        name=logger.name,
        level=level,
        fn="",
        lno=0,
        msg=message,
        args=(),
        exc_info=None
    )
    
    # Añadir información de auditoría al record
    record.user_id = user_id
    record.user_role = user_role
    record.operation_type = operation_type
    record.resource_accessed = resource_accessed
    record.ip_address = ip_address
    record.session_id = session_id
    
    # Añadir datos adicionales
    for key, value in additional_data.items():
        setattr(record, key, value)
    
    logger.handle(record)


def log_consulta_mcp(
    logger: logging.Logger,
    user_id: str,
    user_role: str,
    query_type: str,
    ip_address: Optional[str] = None,
    session_id: Optional[str] = None
) -> None:
    """
    Registra una consulta al servidor MCP según requisito 11.3.
    
    Args:
        logger: Logger a usar.
        user_id: ID anonimizado del usuario.
        user_role: Rol del usuario.
        query_type: Tipo de consulta realizada.
        ip_address: IP del usuario (opcional).
        session_id: ID de la sesión (opcional).
    """
    log_audit_event(
        logger=logger,
        user_id=user_id,
        user_role=user_role,
        operation_type="MCP_QUERY",
        message=f"Consulta MCP realizada: {query_type}",
        resource_accessed="mcp_server",
        ip_address=ip_address,
        session_id=session_id,
        query_type=query_type
    )


def log_intento_escritura(
    logger: logging.Logger,
    user_id: str,
    user_role: str,
    operation_attempted: str,
    ip_address: Optional[str] = None,
    session_id: Optional[str] = None
) -> None:
    """
    Registra un intento de escritura rechazado según requisito 11.4.
    
    Args:
        logger: Logger a usar.
        user_id: ID del usuario que intentó la operación.
        user_role: Rol del usuario.
        operation_attempted: Operación que se intentó realizar.
        ip_address: IP del usuario (opcional).
        session_id: ID de la sesión (opcional).
    """
    log_audit_event(
        logger=logger,
        user_id=user_id,
        user_role=user_role,
        operation_type="WRITE_ATTEMPT_BLOCKED",
        message=f"Intento de escritura bloqueado: {operation_attempted}",
        resource_accessed="mcp_server",
        ip_address=ip_address,
        session_id=session_id,
        level=logging.WARNING,
        operation_attempted=operation_attempted
    )


def log_authentication_event(
    logger: logging.Logger,
    user_id: Optional[str],
    event_type: str,
    success: bool,
    ip_address: Optional[str] = None,
    reason: Optional[str] = None
) -> None:
    """
    Registra eventos de autenticación.
    
    Args:
        logger: Logger a usar.
        user_id: ID del usuario (puede ser None para intentos fallidos).
        event_type: Tipo de evento (LOGIN, LOGOUT, TOKEN_VALIDATION).
        success: Si la operación fue exitosa.
        ip_address: IP del usuario (opcional).
        reason: Razón del fallo (si aplica).
    """
    level = logging.INFO if success else logging.WARNING
    message = f"Evento de autenticación: {event_type} {'exitoso' if success else 'fallido'}"
    
    if reason and not success:
        message += f" - {reason}"
    
    log_audit_event(
        logger=logger,
        user_id=user_id,
        user_role=None,  # Puede no estar disponible durante autenticación
        operation_type=f"AUTH_{event_type}",
        message=message,
        resource_accessed="authentication_system",
        ip_address=ip_address,
        level=level,
        success=success,
        reason=reason
    )


# Logger principal de la aplicación
app_logger = setup_logging()


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Obtiene un logger configurado.
    
    Args:
        name: Nombre del logger. Si es None, usa el logger principal.
        
    Returns:
        logging.Logger: Logger configurado.
    """
    if name:
        return logging.getLogger(f"asistente_cni.{name}")
    return app_logger