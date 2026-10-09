"""
Módulo de modelos de dominio para el sistema de retroalimentación CNI.

Este paquete contiene todos los modelos Pydantic que representan las entidades
del dominio, modelos de autenticación, reportes y enums utilizados en el sistema.
"""

# Enums y tipos
from .enums import (
    Rol, TipoEvento, OpcionRespuesta, EtiquetaVariacion, IntencionConsulta,
    CodigoAnonimo, PorcentajeAciertos, VariacionPuntaje, NumeroSimulacro, NumeroPregunta
)

# Modelos de autenticación
from .auth import (
    TokenResponse, UsuarioAutenticado, CredencialesLogin, RegistroAcceso,
    AuthError, TokenExpiradoError, CredencialesInvalidasError, AccesoNoAutorizadoError
)

# Modelos de dominio
from .dominio import (
    Tema, Grupo, Estudiante, Docente, Simulacro, Pregunta, Respuesta,
    ResultadoTema, VariacionTema
)

# Modelos de reportes
from .reportes import (
    ReporteIndividual, ComparacionDesempeno, OrientacionRefuerzo,
    ReporteGrupal, ResumenInstitucional, ConsultaNLU, RespuestaNLU
)

__all__ = [
    # Enums y tipos
    "Rol", "TipoEvento", "OpcionRespuesta", "EtiquetaVariacion", "IntencionConsulta",
    "CodigoAnonimo", "PorcentajeAciertos", "VariacionPuntaje", "NumeroSimulacro", "NumeroPregunta",
    
    # Modelos de autenticación
    "TokenResponse", "UsuarioAutenticado", "CredencialesLogin", "RegistroAcceso",
    "AuthError", "TokenExpiradoError", "CredencialesInvalidasError", "AccesoNoAutorizadoError",
    
    # Modelos de dominio
    "Tema", "Grupo", "Estudiante", "Docente", "Simulacro", "Pregunta", "Respuesta",
    "ResultadoTema", "VariacionTema",
    
    # Modelos de reportes
    "ReporteIndividual", "ComparacionDesempeno", "OrientacionRefuerzo",
    "ReporteGrupal", "ResumenInstitucional", "ConsultaNLU", "RespuestaNLU"
]