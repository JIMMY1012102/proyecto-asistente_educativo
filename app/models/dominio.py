"""
Modelos de dominio para el sistema de retroalimentación de simulacros CNI.

Este módulo define las entidades principales del negocio: simulacros, preguntas,
respuestas, estudiantes, docentes, materias y temas.
"""

from datetime import datetime, date
from typing import Optional, List, Dict
from pydantic import BaseModel, Field, validator
from decimal import Decimal

from .enums import (
    Rol, OpcionRespuesta, CodigoAnonimo, PorcentajeAciertos, 
    VariacionPuntaje, NumeroSimulacro, NumeroPregunta
)


class Tema(BaseModel):
    """
    Representa un área temática evaluada en los simulacros.
    
    Valida: Requisitos 3.1, 6.1, 7.1, 9.1
    """
    tema_id: int = Field(
        ...,
        description="Identificador único del tema",
        ge=1
    )
    nombre: str = Field(
        ...,
        description="Nombre del tema (ej: Matemáticas, Comprensión Lectora)",
        min_length=1,
        max_length=100
    )
    descripcion: Optional[str] = Field(
        None,
        description="Descripción detallada del tema",
        max_length=255
    )

    class Config:
        json_encoders = {
            # Para compatibilidad con FastAPI
            datetime: lambda v: v.isoformat(),
        }


class Grupo(BaseModel):
    """
    Representa un grupo de estudiantes de 5° de secundaria.
    
    Valida: Requisitos 7.1, 8.1, 9.1
    """
    grupo_id: int = Field(
        ...,
        description="Identificador único del grupo",
        ge=1
    )
    codigo_grupo: str = Field(
        ...,
        description="Código identificador del grupo",
        min_length=1,
        max_length=30
    )
    nivel: str = Field(
        ...,
        description="Nivel educativo (5° secundaria)",
        min_length=1,
        max_length=30
    )
    seccion: str = Field(
        ...,
        description="Sección del grupo (A, B, C, etc.)",
        min_length=1,
        max_length=20
    )
    activo: bool = Field(
        default=True,
        description="Estado activo del grupo"
    )


class Estudiante(BaseModel):
    """
    Representa un estudiante del CNI con datos anonimizados.
    
    Valida: Requisitos 4.1, 8.1, 11.1, 11.5
    """
    usuario_id: int = Field(
        ...,
        description="Identificador único del usuario",
        ge=1
    )
    codigo_anonimo: CodigoAnonimo = Field(
        ...,
        description="Código anonimizado del estudiante (Ley N.º 29733)",
        min_length=1,
        max_length=40
    )
    grupo_id: Optional[int] = Field(
        None,
        description="ID del grupo al que pertenece",
        ge=1
    )
    fecha_asignacion: Optional[date] = Field(
        None,
        description="Fecha de asignación al grupo actual"
    )
    activo: bool = Field(
        default=True,
        description="Estado activo del estudiante"
    )


class Docente(BaseModel):
    """
    Representa un docente con sus grupos asignados.
    
    Valida: Requisitos 7.1, 8.1, 8.3
    """
    usuario_id: int = Field(
        ...,
        description="Identificador único del usuario",
        ge=1
    )
    nombre_usuario: str = Field(
        ...,
        description="Nombre de usuario del docente",
        min_length=1,
        max_length=80
    )
    grupos_asignados: List[int] = Field(
        default_factory=list,
        description="Lista de IDs de grupos asignados al docente"
    )
    activo: bool = Field(
        default=True,
        description="Estado activo del docente"
    )


class Simulacro(BaseModel):
    """
    Representa un simulacro de admisión aplicado a los estudiantes.
    
    Valida: Requisitos 2.1, 4.1, 5.1, 7.1, 9.1
    """
    simulacro_id: int = Field(
        ...,
        description="Identificador único del simulacro",
        ge=1
    )
    nombre: str = Field(
        ...,
        description="Nombre descriptivo del simulacro",
        min_length=1,
        max_length=120
    )
    fecha_aplicacion: date = Field(
        ...,
        description="Fecha en que se aplicó el simulacro"
    )
    fecha_registro: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp de registro en el sistema"
    )
    descripcion: Optional[str] = Field(
        None,
        description="Descripción adicional del simulacro",
        max_length=255
    )
    grupos_participantes: Optional[List[int]] = Field(
        default_factory=list,
        description="IDs de los grupos que participaron en este simulacro"
    )

    # Nota: Removido validador de fecha futura para permitir simulacros programados


class Pregunta(BaseModel):
    """
    Representa una pregunta específica dentro de un simulacro.
    
    Valida: Requisitos 2.5, 3.1, 3.3, 3.5
    """
    pregunta_id: int = Field(
        ...,
        description="Identificador único de la pregunta",
        ge=1
    )
    simulacro_id: int = Field(
        ...,
        description="ID del simulacro al que pertenece",
        ge=1
    )
    tema_id: int = Field(
        ...,
        description="ID del tema al que pertenece",
        ge=1
    )
    numero_pregunta: NumeroPregunta = Field(
        ...,
        description="Número de la pregunta dentro del simulacro",
        ge=1
    )
    opcion_correcta: OpcionRespuesta = Field(
        ...,
        description="Opción correcta (A, B, C, D, E)"
    )


class Respuesta(BaseModel):
    """
    Representa la respuesta de un estudiante a una pregunta específica.
    
    Valida: Requisitos 2.1, 3.1, 4.1, 5.1, 7.1, 8.1, 9.1
    """
    usuario_id: int = Field(
        ...,
        description="ID del estudiante que respondió",
        ge=1
    )
    pregunta_id: int = Field(
        ...,
        description="ID de la pregunta respondida",
        ge=1
    )
    opcion_seleccionada: OpcionRespuesta = Field(
        ...,
        description="Opción seleccionada por el estudiante"
    )
    fecha_registro: datetime = Field(
        default_factory=datetime.now,
        description="Timestamp del registro de la respuesta"
    )
    es_correcta: Optional[bool] = Field(
        None,
        description="Indica si la respuesta es correcta (calculado)"
    )


class ResultadoTema(BaseModel):
    """
    Resultado agregado de un estudiante en un tema específico.
    
    Valida: Requisitos 3.1, 3.2, 4.2, 5.1
    """
    tema_id: int = Field(
        ...,
        description="ID del tema",
        ge=1
    )
    nombre_tema: str = Field(
        ...,
        description="Nombre del tema",
        min_length=1
    )
    preguntas_totales: int = Field(
        ...,
        description="Total de preguntas del tema en el simulacro",
        ge=0
    )
    respuestas_correctas: int = Field(
        ...,
        description="Número de respuestas correctas",
        ge=0
    )
    respuestas_incorrectas: int = Field(
        ...,
        description="Número de respuestas incorrectas",
        ge=0
    )
    porcentaje_aciertos: PorcentajeAciertos = Field(
        ...,
        description="Porcentaje de aciertos (0.0-100.0)",
        ge=0.0,
        le=100.0
    )

    @validator('respuestas_correctas')
    def validar_respuestas_correctas(cls, v, values):
        """Valida que las respuestas correctas no excedan el total."""
        preguntas_totales = values.get('preguntas_totales', 0)
        if v > preguntas_totales:
            raise ValueError("Respuestas correctas no pueden exceder total de preguntas")
        return v

    @validator('respuestas_incorrectas')
    def validar_respuestas_incorrectas(cls, v, values):
        """Valida que las respuestas incorrectas sean consistentes."""
        preguntas_totales = values.get('preguntas_totales', 0)
        respuestas_correctas = values.get('respuestas_correctas', 0)
        if v > (preguntas_totales - respuestas_correctas):
            raise ValueError("Respuestas incorrectas inconsistentes con total")
        return v

    @validator('porcentaje_aciertos')
    def validar_porcentaje_aciertos(cls, v, values):
        """Valida que el porcentaje sea consistente con los contadores."""
        preguntas_totales = values.get('preguntas_totales', 0)
        respuestas_correctas = values.get('respuestas_correctas', 0)
        
        if preguntas_totales == 0:
            if v != 0.0:
                raise ValueError("Porcentaje debe ser 0 cuando no hay preguntas")
        else:
            porcentaje_esperado = (respuestas_correctas / preguntas_totales) * 100
            # Permitir pequeñas diferencias por redondeo
            if abs(v - porcentaje_esperado) > 0.1:
                raise ValueError(f"Porcentaje inconsistente: esperado {porcentaje_esperado:.1f}, recibido {v}")
        
        return round(v, 1)


class VariacionTema(BaseModel):
    """
    Variación de puntaje entre simulacros para un tema específico.
    
    Valida: Requisitos 5.1, 5.2, 8.1
    """
    tema_id: int = Field(
        ...,
        description="ID del tema",
        ge=1
    )
    nombre_tema: str = Field(
        ...,
        description="Nombre del tema",
        min_length=1
    )
    puntaje_anterior: int = Field(
        ...,
        description="Puntaje en el simulacro anterior",
        ge=0
    )
    puntaje_actual: int = Field(
        ...,
        description="Puntaje en el simulacro actual",
        ge=0
    )
    variacion_absoluta: VariacionPuntaje = Field(
        default=0,
        description="Diferencia absoluta entre puntajes"
    )
    etiqueta: str = Field(
        default="",
        description="Etiqueta de la variación (Mejora/Retroceso/Sin cambio)",
        min_length=0
    )

    @validator('variacion_absoluta', always=True)
    def calcular_variacion(cls, v, values):
        """Calcula automáticamente la variación absoluta."""
        puntaje_actual = values.get('puntaje_actual', 0)
        puntaje_anterior = values.get('puntaje_anterior', 0)
        return puntaje_actual - puntaje_anterior

    @validator('etiqueta', always=True)
    def calcular_etiqueta(cls, v, values):
        """Calcula automáticamente la etiqueta según la variación."""
        variacion = values.get('variacion_absoluta', 0)
        if variacion > 0:
            return "Mejora"
        elif variacion < 0:
            return "Retroceso"
        else:
            return "Sin cambio"