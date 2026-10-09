"""
Enums y constantes para el sistema de retroalimentación de simulacros CNI.

Este módulo define todos los enums, constantes y tipos de datos utilizados
en el dominio del sistema. Incluye roles de usuario, tipos de eventos,
opciones de respuesta y otros valores categóricos.
"""

from enum import Enum
from typing import Literal


class Rol(str, Enum):
    """
    Roles de usuario en el sistema CNI.
    
    Valida: Requisitos 1.1, 1.2
    """
    ESTUDIANTE = "estudiante"
    DOCENTE = "docente" 
    DIRECCION = "direccion"


class TipoEvento(str, Enum):
    """
    Tipos de eventos para el registro de auditoría.
    
    Valida: Requisitos 11.3, 11.4
    """
    CONSULTA_DATOS = "consulta_datos"
    INTENTO_ESCRITURA = "intento_escritura"
    ACCESO_DENEGADO = "acceso_denegado"
    INICIO_SESION = "inicio_sesion"


class OpcionRespuesta(str, Enum):
    """
    Opciones de respuesta válidas para las preguntas de simulacro.
    
    Valida: Requisitos 2.1, 3.1
    """
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    E = "E"


class EtiquetaVariacion(str, Enum):
    """
    Etiquetas para clasificar la variación de puntaje entre simulacros.
    
    Valida: Requisitos 5.1, 5.2
    """
    MEJORA = "Mejora"
    RETROCESO = "Retroceso"
    SIN_CAMBIO = "Sin cambio"


class IntencionConsulta(str, Enum):
    """
    Intenciones de consulta clasificadas por la Gemini API.
    
    Valida: Requisitos 10.1, 10.5, 10.6
    """
    REPORTE_INDIVIDUAL = "reporte_individual"
    COMPARACION_DESEMPENO = "comparacion_desempeno"
    ORIENTACION_REFUERZO = "orientacion_refuerzo"
    REPORTE_GRUPAL = "reporte_grupal"
    DETALLE_ESTUDIANTE = "detalle_estudiante"
    RESUMEN_INSTITUCIONAL = "resumen_institucional"
    NO_RECONOCIDA = "no_reconocida"


# Alias de tipos para mejorar la legibilidad
CodigoAnonimo = str
"""Código anónimo del estudiante para cumplir con Ley N.º 29733"""

PorcentajeAciertos = float
"""Porcentaje de aciertos expresado como decimal entre 0.0 y 100.0"""

VariacionPuntaje = int
"""Variación de puntaje entre simulacros expresada en puntos absolutos"""

NumeroSimulacro = int
"""Identificador numérico del simulacro"""

NumeroPregunta = int
"""Número de pregunta dentro de un simulacro (1-based)"""