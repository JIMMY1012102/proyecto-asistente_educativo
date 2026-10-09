"""
Modelos para reportes y respuestas del sistema de retroalimentación CNI.

Este módulo define los modelos de datos para los diferentes tipos de reportes
que genera el sistema: individuales, grupales e institucionales.
"""

from datetime import date, datetime
from typing import List, Optional, Dict
from pydantic import BaseModel, Field, validator

from .enums import CodigoAnonimo, PorcentajeAciertos, EtiquetaVariacion
from .dominio import ResultadoTema, VariacionTema


class ReporteIndividual(BaseModel):
    """
    Reporte de retroalimentación individual para un estudiante.
    
    Valida: Requisitos 4.1, 4.2, 4.5, 8.2
    """
    estudiante_codigo: CodigoAnonimo = Field(
        ...,
        description="Código anonimizado del estudiante"
    )
    simulacro_id: int = Field(
        ...,
        description="ID del simulacro reportado",
        ge=1
    )
    nombre_simulacro: str = Field(
        ...,
        description="Nombre del simulacro",
        min_length=1
    )
    fecha_aplicacion: date = Field(
        ...,
        description="Fecha de aplicación del simulacro"
    )
    puntaje_total: int = Field(
        ...,
        description="Respuestas correctas totales",
        ge=0
    )
    preguntas_totales: int = Field(
        ...,
        description="Total de preguntas en el simulacro",
        ge=1
    )
    porcentaje_global: PorcentajeAciertos = Field(
        ...,
        description="Porcentaje de aciertos global (0.0-100.0)",
        ge=0.0,
        le=100.0
    )
    resultados_por_tema: List[ResultadoTema] = Field(
        ...,
        description="Resultados detallados por tema, ordenados de menor a mayor porcentaje"
    )
    temas_con_errores: List[str] = Field(
        default_factory=list,
        description="Lista de nombres de temas donde el estudiante cometió errores"
    )

    @validator('puntaje_total')
    def validar_puntaje_total(cls, v, values):
        """Valida que el puntaje total no exceda las preguntas totales."""
        preguntas_totales = values.get('preguntas_totales', 0)
        if preguntas_totales > 0 and v > preguntas_totales:
            raise ValueError("Puntaje total no puede exceder preguntas totales")
        return v

    @validator('porcentaje_global')
    def validar_porcentaje_global(cls, v, values):
        """Valida que el porcentaje global sea consistente."""
        puntaje_total = values.get('puntaje_total', 0)
        preguntas_totales = values.get('preguntas_totales', 1)
        
        # Solo validar si tenemos ambos valores
        if puntaje_total is not None and preguntas_totales > 0:
            porcentaje_esperado = (puntaje_total / preguntas_totales) * 100
            # Permitir pequeñas diferencias por redondeo
            if abs(v - porcentaje_esperado) > 0.1:
                raise ValueError(f"Porcentaje global inconsistente: esperado {porcentaje_esperado:.1f}%, recibido {v}%")
        
        return round(v, 1)

    @validator('temas_con_errores', always=True)
    def validar_temas_con_errores(cls, v, values):
        """Genera automáticamente la lista de temas con errores si está vacía."""
        # Si ya se proporcionó una lista no vacía, mantenerla
        if v:
            return v
        
        # Sino, generar automáticamente desde resultados_por_tema
        resultados = values.get('resultados_por_tema', [])
        temas_errores = [
            resultado.nombre_tema 
            for resultado in resultados 
            if resultado.respuestas_incorrectas > 0
        ]
        return temas_errores


class ComparacionDesempeno(BaseModel):
    """
    Comparación de desempeño entre dos simulacros consecutivos.
    
    Valida: Requisitos 5.1, 5.2, 8.1
    """
    estudiante_codigo: CodigoAnonimo = Field(
        ...,
        description="Código anonimizado del estudiante"
    )
    simulacro_anterior_id: int = Field(
        ...,
        description="ID del simulacro anterior",
        ge=1
    )
    simulacro_actual_id: int = Field(
        ...,
        description="ID del simulacro más reciente",
        ge=1
    )
    fecha_anterior: date = Field(
        ...,
        description="Fecha del simulacro anterior"
    )
    fecha_actual: date = Field(
        ...,
        description="Fecha del simulacro actual"
    )
    variaciones_por_tema: List[VariacionTema] = Field(
        ...,
        description="Variaciones de puntaje por tema"
    )
    puntaje_total_anterior: int = Field(
        ...,
        description="Puntaje total en simulacro anterior",
        ge=0
    )
    puntaje_total_actual: int = Field(
        ...,
        description="Puntaje total en simulacro actual",
        ge=0
    )
    variacion_total: int = Field(
        ...,
        description="Variación total de puntaje"
    )

    @validator('fecha_actual')
    def validar_fechas_orden(cls, v, values):
        """Valida que el simulacro actual sea posterior al anterior."""
        fecha_anterior = values.get('fecha_anterior')
        if fecha_anterior and v <= fecha_anterior:
            raise ValueError("Simulacro actual debe ser posterior al anterior")
        return v


class OrientacionRefuerzo(BaseModel):
    """
    Orientación de refuerzo basada en temas con menor desempeño.
    
    Valida: Requisitos 6.1, 6.4
    """
    estudiante_codigo: CodigoAnonimo = Field(
        ...,
        description="Código anonimizado del estudiante"
    )
    simulacro_id: int = Field(
        ...,
        description="ID del simulacro base para la orientación",
        ge=1
    )
    temas_priorizados: List[ResultadoTema] = Field(
        ...,
        description="Temas ordenados por prioridad de refuerzo (menor a mayor porcentaje)"
    )
    mensaje_orientacion: str = Field(
        ...,
        description="Mensaje explicativo para el estudiante",
        min_length=1
    )

    @validator('temas_priorizados')
    def validar_orden_prioridad(cls, v):
        """Valida que los temas estén ordenados correctamente por prioridad."""
        if len(v) <= 1:
            return v
        
        for i in range(len(v) - 1):
            if v[i].porcentaje_aciertos > v[i + 1].porcentaje_aciertos:
                raise ValueError("Temas deben estar ordenados de menor a mayor porcentaje")
            elif (v[i].porcentaje_aciertos == v[i + 1].porcentaje_aciertos and 
                  v[i].respuestas_incorrectas < v[i + 1].respuestas_incorrectas):
                raise ValueError("En caso de empate, ordenar por mayor número de errores")
        
        return v


class ReporteGrupal(BaseModel):
    """
    Reporte agregado de errores por tema para un grupo de estudiantes.
    
    Valida: Requisitos 7.1, 7.2, 7.3
    """
    grupo_id: int = Field(
        ...,
        description="ID del grupo reportado",
        ge=1
    )
    codigo_grupo: str = Field(
        ...,
        description="Código del grupo",
        min_length=1
    )
    simulacro_id: int = Field(
        ...,
        description="ID del simulacro reportado",
        ge=1
    )
    nombre_simulacro: str = Field(
        ...,
        description="Nombre del simulacro",
        min_length=1
    )
    fecha_aplicacion: date = Field(
        ...,
        description="Fecha de aplicación del simulacro"
    )
    estudiantes_incluidos: int = Field(
        ...,
        description="Número de estudiantes incluidos en el cálculo",
        ge=1
    )
    porcentajes_error_por_tema: List[Dict[str, float]] = Field(
        ...,
        description="Porcentajes de error por tema, ordenados de mayor a menor error"
    )
    temas_mayor_debilidad: List[str] = Field(
        ...,
        description="Nombres de temas con mayor porcentaje de error del grupo"
    )

    @validator('porcentajes_error_por_tema')
    def validar_orden_error(cls, v):
        """Valida que los temas estén ordenados de mayor a menor porcentaje de error."""
        if len(v) <= 1:
            return v
        
        for i in range(len(v) - 1):
            porcentaje_actual = list(v[i].values())[0]
            porcentaje_siguiente = list(v[i + 1].values())[0]
            if porcentaje_actual < porcentaje_siguiente:
                raise ValueError("Temas deben estar ordenados de mayor a menor error")
        
        return v


class ResumenInstitucional(BaseModel):
    """
    Resumen agregado de resultados a nivel institucional (solo datos agregados).
    
    Valida: Requisitos 9.1, 9.2, 9.4, 11.5
    """
    simulacro_id: int = Field(
        ...,
        description="ID del simulacro reportado",
        ge=1
    )
    nombre_simulacro: str = Field(
        ...,
        description="Nombre del simulacro",
        min_length=1
    )
    fecha_aplicacion: date = Field(
        ...,
        description="Fecha de aplicación del simulacro"
    )
    grupos_incluidos: int = Field(
        ...,
        description="Número de grupos de 5° secundaria incluidos",
        ge=0
    )
    estudiantes_incluidos: int = Field(
        ...,
        description="Total de estudiantes incluidos en el cálculo",
        ge=0
    )
    porcentajes_error_institucional: List[Dict[str, float]] = Field(
        ...,
        description="Porcentajes de error por tema a nivel institucional"
    )
    temas_refuerzo_institucional: List[str] = Field(
        ...,
        description="Temas que requieren refuerzo a nivel institucional"
    )
    grupos_excluidos: int = Field(
        default=0,
        description="Número de grupos excluidos por falta de resultados",
        ge=0
    )

    @validator('estudiantes_incluidos')
    def validar_estudiantes_grupos(cls, v, values):
        """Valida consistencia entre estudiantes y grupos."""
        grupos_incluidos = values.get('grupos_incluidos', 0)
        if grupos_incluidos == 0 and v > 0:
            raise ValueError("No puede haber estudiantes sin grupos")
        return v

    class Config:
        json_encoders = {
            date: lambda v: v.isoformat(),
            datetime: lambda v: v.isoformat(),
        }


class ConsultaNLU(BaseModel):
    """
    Consulta en lenguaje natural enviada por un usuario.
    
    Valida: Requisitos 10.1, 10.5, 10.6
    """
    texto_consulta: str = Field(
        ...,
        description="Texto de la consulta en español",
        min_length=1,
        max_length=500,
        strip_whitespace=True
    )
    rol_usuario: str = Field(
        ...,
        description="Rol del usuario que hace la consulta"
    )
    usuario_id: Optional[int] = Field(
        None,
        description="ID del usuario autenticado",
        ge=1
    )

    @validator('texto_consulta')
    def validar_texto_no_vacio(cls, v):
        """Valida que el texto no esté vacío después del strip."""
        if not v or v.isspace():
            raise ValueError("Texto de consulta no puede estar vacío")
        return v


class RespuestaNLU(BaseModel):
    """
    Respuesta del sistema a una consulta en lenguaje natural.
    
    Valida: Requisitos 10.1, 10.4
    """
    intencion_clasificada: str = Field(
        ...,
        description="Intención clasificada por Gemini API",
        min_length=1
    )
    respuesta_generada: str = Field(
        ...,
        description="Respuesta generada por el sistema",
        min_length=1
    )
    datos_adjuntos: Optional[Dict] = Field(
        None,
        description="Datos estructurados relacionados con la respuesta"
    )
    tiempo_procesamiento: float = Field(
        ...,
        description="Tiempo de procesamiento en segundos",
        ge=0.0
    )
    exito: bool = Field(
        ...,
        description="Indica si la consulta se procesó exitosamente"
    )