# Asistente de Retroalimentación para Simulacros de Admisión — CNI

**Versión:** v1 — Semana 6
**Fecha:** 2026-10-09

## Diagrama de secuencia — R2

```mermaid
sequenceDiagram
    actor Docente as Docente (Navegador)
    participant Router as Enrutador CI4
    participant FiltroAuth as Filtro Autenticación
    participant FiltroRol as Filtro Rol
    participant CtrlDocente as Controlador Docente
    participant SvcReporte as Servicio Reportes
    participant SvcCalculo as Servicio Cálculos
    participant SvcAuditoria as Servicio Auditoría
    participant ModeloSim as Modelo Simulacro
    participant ModeloResp as Modelo Respuesta
    participant ModeloReg as Modelo Registro Acceso
    participant MySQL as MySQL / MariaDB
    participant Vista as Vista HTML (Navegador)

    Docente->>Router: POST /docente/simulacro/{id}/procesar

    Router->>FiltroAuth: verificarSesion(token)
    FiltroAuth->>MySQL: SELECT usuario WHERE session_token = ?
    MySQL-->>FiltroAuth: fila usuario (rol = Docente)
    FiltroAuth-->>Router: sesión válida

    Router->>FiltroRol: verificarRol(Docente)
    FiltroRol-->>Router: rol autorizado

    Router->>CtrlDocente: procesarSimulacro(id_simulacro)

    CtrlDocente->>SvcReporte: generarReporteGrupal(id_docente, id_simulacro)

    SvcReporte->>ModeloSim: obtenerSimulacro(id_simulacro)
    ModeloSim->>MySQL: SELECT * FROM simulacro WHERE simulacro_id = ?
    MySQL-->>ModeloSim: datos simulacro
    alt simulacro no existe
        ModeloSim-->>SvcReporte: null
        SvcReporte-->>CtrlDocente: error «simulacro no encontrado»
        CtrlDocente-->>Vista: mensaje de error al Docente
    else simulacro encontrado
        ModeloSim-->>SvcReporte: objeto Simulacro
    end

    SvcReporte->>ModeloSim: obtenerGruposDelDocente(id_docente)
    ModeloSim->>MySQL: SELECT grupo_id FROM docente_grupo WHERE usuario_id = ?
    MySQL-->>ModeloSim: lista grupos

    SvcReporte->>ModeloResp: obtenerRespuestasPorSimulacro(id_simulacro, grupos)
    ModeloResp->>MySQL: SELECT r.*, p.tema_id, p.opcion_correcta\n  FROM respuesta r\n  JOIN pregunta p ON r.pregunta_id = p.pregunta_id\n  WHERE p.simulacro_id = ?\n    AND r.usuario_id IN (estudiantes de los grupos)
    MySQL-->>ModeloResp: filas de respuestas

    alt respuesta vacía o timeout > 5 s
        ModeloResp-->>SvcReporte: error de servicio
        SvcReporte->>SvcAuditoria: registrarError(id_docente, tipo, timestamp, codigo)
        SvcAuditoria->>ModeloReg: insertar registro_acceso
        ModeloReg->>MySQL: INSERT INTO registro_acceso ...
        MySQL-->>ModeloReg: ok
        SvcReporte-->>CtrlDocente: «servicio de datos no disponible temporalmente»
        CtrlDocente-->>Vista: mensaje de error al Docente
    else respuestas recibidas
        ModeloResp-->>SvcReporte: lista Respuestas
    end

    SvcReporte->>SvcCalculo: calcularPorcentajePorTema(respuestas, preguntas)
    note over SvcCalculo: Para cada Estudiante × Tema:\n  aciertos / total_preguntas_tema × 100\n  Omitir registros con campos nulos
    SvcCalculo-->>SvcReporte: mapa [tema → % aciertos] por Estudiante

    SvcReporte->>SvcCalculo: ordenarPorPorcentajeAscendente(resultados)
    SvcCalculo-->>SvcReporte: temas ordenados de menor a mayor acierto

    SvcReporte->>SvcAuditoria: registrarConsulta(id_docente, Docente, procesamiento_simulacro, timestamp)
    SvcAuditoria->>ModeloReg: insertar registro_acceso (sin contenido de resultados)
    ModeloReg->>MySQL: INSERT INTO registro_acceso ...
    MySQL-->>ModeloReg: ok

    SvcReporte-->>CtrlDocente: ReporteGrupal (simulacro, temas ordenados, n.º omitidos)
    CtrlDocente->>Vista: renderizar vista con datos del reporte
    Vista-->>Docente: HTML con clasificación de errores por tema
```
