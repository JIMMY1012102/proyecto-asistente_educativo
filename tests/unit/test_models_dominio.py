"""
Pruebas unitarias para los modelos de dominio del sistema CNI.

Valida que los modelos Pydantic funcionen correctamente con datos válidos
e invaliden datos incorrectos según las reglas de negocio definidas.
"""

import pytest
from datetime import datetime, date
from pydantic import ValidationError

from app.models import (
    Rol, OpcionRespuesta, Tema, Grupo, Estudiante, Docente, 
    Simulacro, Pregunta, Respuesta, ResultadoTema, VariacionTema,
    ReporteIndividual, ComparacionDesempeno
)


class TestEnums:
    """Pruebas para los enums del sistema."""
    
    def test_rol_valores_validos(self):
        """Verifica que los roles sean válidos."""
        assert Rol.ESTUDIANTE == "estudiante"
        assert Rol.DOCENTE == "docente"
        assert Rol.DIRECCION == "direccion"
    
    def test_opcion_respuesta_valores_validos(self):
        """Verifica que las opciones de respuesta sean válidas."""
        assert OpcionRespuesta.A == "A"
        assert OpcionRespuesta.B == "B"
        assert OpcionRespuesta.C == "C"
        assert OpcionRespuesta.D == "D"
        assert OpcionRespuesta.E == "E"


class TestTema:
    """Pruebas para el modelo Tema."""
    
    def test_tema_valido(self):
        """Prueba creación de tema válido."""
        tema = Tema(
            tema_id=1,
            nombre="Matemáticas",
            descripcion="Álgebra, geometría y trigonometría"
        )
        assert tema.tema_id == 1
        assert tema.nombre == "Matemáticas"
        assert tema.descripcion == "Álgebra, geometría y trigonometría"
    
    def test_tema_sin_descripcion(self):
        """Prueba tema sin descripción (opcional)."""
        tema = Tema(tema_id=1, nombre="Comprensión Lectora")
        assert tema.descripcion is None
    
    def test_tema_id_invalido(self):
        """Prueba que tema_id debe ser mayor a 0."""
        with pytest.raises(ValidationError):
            Tema(tema_id=0, nombre="Test")
    
    def test_nombre_vacio(self):
        """Prueba que el nombre no puede estar vacío."""
        with pytest.raises(ValidationError):
            Tema(tema_id=1, nombre="")


class TestGrupo:
    """Pruebas para el modelo Grupo."""
    
    def test_grupo_valido(self):
        """Prueba creación de grupo válido."""
        grupo = Grupo(
            grupo_id=1,
            codigo_grupo="5A-2024",
            nivel="5° secundaria",
            seccion="A"
        )
        assert grupo.grupo_id == 1
        assert grupo.codigo_grupo == "5A-2024"
        assert grupo.activo is True  # valor por defecto


class TestEstudiante:
    """Pruebas para el modelo Estudiante."""
    
    def test_estudiante_valido(self):
        """Prueba creación de estudiante válido."""
        estudiante = Estudiante(
            usuario_id=1,
            codigo_anonimo="EST001_2024",
            grupo_id=1,
            fecha_asignacion=date(2024, 3, 1)
        )
        assert estudiante.usuario_id == 1
        assert estudiante.codigo_anonimo == "EST001_2024"
        assert estudiante.activo is True


class TestSimulacro:
    """Pruebas para el modelo Simulacro."""
    
    def test_simulacro_valido(self):
        """Prueba creación de simulacro válido."""
        simulacro = Simulacro(
            simulacro_id=1,
            nombre="Simulacro Nacional - Marzo 2024",
            fecha_aplicacion=date(2024, 3, 15),
            descripcion="Primer simulacro del año académico"
        )
        assert simulacro.simulacro_id == 1
        assert simulacro.nombre == "Simulacro Nacional - Marzo 2024"
        assert simulacro.fecha_aplicacion == date(2024, 3, 15)
    
    def test_fecha_futura_permitida(self):
        """Prueba que la fecha de aplicación futura es permitida para simulacros programados."""
        fecha_futura = date(2025, 12, 31)
        simulacro = Simulacro(
            simulacro_id=1,
            nombre="Test Futuro",
            fecha_aplicacion=fecha_futura
        )
        assert simulacro.fecha_aplicacion == fecha_futura


class TestPregunta:
    """Pruebas para el modelo Pregunta."""
    
    def test_pregunta_valida(self):
        """Prueba creación de pregunta válida."""
        pregunta = Pregunta(
            pregunta_id=1,
            simulacro_id=1,
            tema_id=1,
            numero_pregunta=1,
            opcion_correcta=OpcionRespuesta.A
        )
        assert pregunta.pregunta_id == 1
        assert pregunta.numero_pregunta == 1
        assert pregunta.opcion_correcta == OpcionRespuesta.A
    
    def test_numero_pregunta_invalido(self):
        """Prueba que el número de pregunta debe ser mayor a 0."""
        with pytest.raises(ValidationError):
            Pregunta(
                pregunta_id=1,
                simulacro_id=1,
                tema_id=1,
                numero_pregunta=0,
                opcion_correcta=OpcionRespuesta.A
            )


class TestRespuesta:
    """Pruebas para el modelo Respuesta."""
    
    def test_respuesta_valida(self):
        """Prueba creación de respuesta válida."""
        respuesta = Respuesta(
            usuario_id=1,
            pregunta_id=1,
            opcion_seleccionada=OpcionRespuesta.B
        )
        assert respuesta.usuario_id == 1
        assert respuesta.pregunta_id == 1
        assert respuesta.opcion_seleccionada == OpcionRespuesta.B


class TestResultadoTema:
    """Pruebas para el modelo ResultadoTema."""
    
    def test_resultado_tema_valido(self):
        """Prueba creación de resultado tema válido."""
        resultado = ResultadoTema(
            tema_id=1,
            nombre_tema="Matemáticas",
            preguntas_totales=10,
            respuestas_correctas=8,
            respuestas_incorrectas=2,
            porcentaje_aciertos=80.0
        )
        assert resultado.tema_id == 1
        assert resultado.porcentaje_aciertos == 80.0
    
    def test_porcentaje_inconsistente(self):
        """Prueba validación de porcentaje inconsistente."""
        with pytest.raises(ValidationError):
            ResultadoTema(
                tema_id=1,
                nombre_tema="Test",
                preguntas_totales=10,
                respuestas_correctas=8,
                respuestas_incorrectas=2,
                porcentaje_aciertos=90.0  # Inconsistente con 8/10
            )
    
    def test_respuestas_correctas_exceden_total(self):
        """Prueba que respuestas correctas no excedan total."""
        with pytest.raises(ValidationError):
            ResultadoTema(
                tema_id=1,
                nombre_tema="Test",
                preguntas_totales=10,
                respuestas_correctas=15,  # Mayor que total
                respuestas_incorrectas=0,
                porcentaje_aciertos=100.0
            )


class TestVariacionTema:
    """Pruebas para el modelo VariacionTema."""
    
    def test_variacion_tema_mejora(self):
        """Prueba cálculo automático de mejora."""
        variacion = VariacionTema(
            tema_id=1,
            nombre_tema="Matemáticas",
            puntaje_anterior=6,
            puntaje_actual=8
        )
        assert variacion.variacion_absoluta == 2
        assert variacion.etiqueta == "Mejora"
    
    def test_variacion_tema_retroceso(self):
        """Prueba cálculo automático de retroceso."""
        variacion = VariacionTema(
            tema_id=1,
            nombre_tema="Ciencias",
            puntaje_anterior=8,
            puntaje_actual=5
        )
        assert variacion.variacion_absoluta == -3
        assert variacion.etiqueta == "Retroceso"
    
    def test_variacion_tema_sin_cambio(self):
        """Prueba cálculo automático de sin cambio."""
        variacion = VariacionTema(
            tema_id=1,
            nombre_tema="Historia",
            puntaje_anterior=7,
            puntaje_actual=7
        )
        assert variacion.variacion_absoluta == 0
        assert variacion.etiqueta == "Sin cambio"


class TestReporteIndividual:
    """Pruebas para el modelo ReporteIndividual."""
    
    def test_reporte_individual_valido(self):
        """Prueba creación de reporte individual válido."""
        resultado1 = ResultadoTema(
            tema_id=1,
            nombre_tema="Matemáticas",
            preguntas_totales=10,
            respuestas_correctas=8,
            respuestas_incorrectas=2,
            porcentaje_aciertos=80.0
        )
        
        resultado2 = ResultadoTema(
            tema_id=2,
            nombre_tema="Ciencias",
            preguntas_totales=10,
            respuestas_correctas=6,
            respuestas_incorrectas=4,
            porcentaje_aciertos=60.0
        )
        
        # Puntaje total = 8 + 6 = 14 respuestas correctas de 20 preguntas = 70%
        reporte = ReporteIndividual(
            estudiante_codigo="EST001",
            simulacro_id=1,
            nombre_simulacro="Test Marzo",
            fecha_aplicacion=date(2024, 3, 15),
            puntaje_total=14,
            preguntas_totales=20,
            porcentaje_global=70.0,
            resultados_por_tema=[resultado2, resultado1]  # Ordenar por porcentaje ascendente (60%, 80%)
        )
        
        assert reporte.puntaje_total == 14
        assert reporte.porcentaje_global == 70.0
        assert len(reporte.temas_con_errores) == 2  # Ambos temas tienen errores
        assert "Matemáticas" in reporte.temas_con_errores
        assert "Ciencias" in reporte.temas_con_errores
    
    def test_puntaje_excede_total(self):
        """Prueba que el puntaje no exceda preguntas totales."""
        with pytest.raises(ValidationError):
            ReporteIndividual(
                estudiante_codigo="EST001",
                simulacro_id=1,
                nombre_simulacro="Test",
                fecha_aplicacion=date(2024, 3, 15),
                puntaje_total=21,  # Mayor que total
                preguntas_totales=20,
                porcentaje_global=100.0,
                resultados_por_tema=[]
            )