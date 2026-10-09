# Implementation Plan: Asistente de Retroalimentación para Simulacros de Admisión

## Overview

Este plan implementa el Asistente de Retroalimentación para Simulacros de Admisión del CNI como una aplicación web FastAPI con frontend HTML+JavaScript. El sistema procesa automáticamente los resultados de simulacros consultando el servidor MCP de solo lectura y proporciona retroalimentación personalizada por rol (Estudiante, Docente, Dirección) con apoyo de la Gemini API para consultas en lenguaje natural.

## Tasks

- [x] 1. Configuración inicial del proyecto y estructura de directorios
  - Crear estructura de directorios según el diseño
  - Configurar entorno virtual de Python 3.11+
  - Instalar dependencias básicas (FastAPI, uvicorn, python-jose, passlib, httpx)
  - Crear archivos de configuración (.env.example, requirements.txt, .gitignore)
  - _Requisitos: 11.1, 10.2_

- [x] 2. Implementar módulo de autenticación y control de acceso
  - [x] 2.1 Crear modelos de datos de autenticación
    - Implementar dataclasses: TokenResponse, UsuarioAutenticado, Rol
    - Definir excepciones de autenticación: AuthError, TokenExpiradoError, etc.
    - _Requisitos: 1.1, 1.2_
  
  - [ ]* 2.2 Escribir prueba de propiedad para autenticación de roles
    - **Propiedad 1: Autenticación devuelve el rol correcto**
    - **Valida: Requisitos 1.1**
  
  - [x] 2.3 Implementar funciones de autenticación JWT
    - Crear función autenticar() con validación de credenciales
    - Implementar verificar_token() con validación de firma y expiración
    - Crear verificar_acceso_rol() con control de acceso por recurso
    - _Requisitos: 1.1, 1.3, 1.4_
  
  - [ ]* 2.4 Escribir pruebas de propiedades para control de acceso
    - **Propiedad 2: Rechazo de credenciales inválidas sin revelar campo**
    - **Valida: Requisitos 1.2**
    - **Propiedad 3: Control de acceso por rol**
    - **Valida: Requisitos 1.5, 1.6, 1.7**
    - **Propiedad 4: Validación de token en cada solicitud**
    - **Valida: Requisitos 1.3, 1.4**

- [ ] 3. Checkpoint - Verificar autenticación básica
  - Asegurar que todas las pruebas pasan, preguntar al usuario si surgen dudas.

- [ ] 4. Implementar cliente MCP y manejo de datos
  - [x] 4.1 Crear modelos de dominio
    - Implementar dataclasses: Simulacro, RespuestaEstudiante, ResultadoTema
    - Crear modelos de reportes: ReporteIndividual, ReporteGrupal, ResumenInstitucional
    - _Requisitos: 2.1, 3.1_
  
  - [ ] 4.2 Implementar cliente MCP
    - Crear funciones de consulta: obtener_respuestas_simulacro(), obtener_simulacros_estudiante()
    - Implementar obtener_simulacros_grupo(), obtener_simulacros_institucion()
    - Manejar timeouts y errores de conexión
    - _Requisitos: 2.2, 2.3, 2.4_
  
  - [ ]* 4.3 Escribir pruebas de propiedades para manejo de errores MCP
    - **Propiedad 5: Manejo de errores del Servidor MCP**
    - **Valida: Requisitos 2.3, 8.5**
    - **Propiedad 6: Filtrado de registros inválidos en el procesamiento**
    - **Valida: Requisitos 2.5**

- [ ] 5. Implementar módulo de lógica de negocio
  - [ ] 5.1 Crear funciones de cálculo
    - Implementar calcular_porcentaje_aciertos() con precisión de 1 decimal
    - Crear calcular_variacion_puntaje() para comparación entre simulacros
    - Implementar funciones de agregación para reportes grupales e institucionales
    - _Requisitos: 3.1, 5.1, 7.1, 9.1_
  
  - [ ]* 5.2 Escribir pruebas de propiedades para cálculos
    - **Propiedad 7: Cálculo correcto del Porcentaje de Aciertos**
    - **Valida: Requisitos 3.1, 3.5**
    - **Propiedad 11: Cálculo correcto de la Variación de Puntaje y etiqueta**
    - **Valida: Requisitos 5.1, 5.2**
  
  - [ ] 5.3 Implementar funciones de ordenamiento
    - Crear ordenar_temas_por_porcentaje_asc() con criterios de empate
    - Implementar ordenar_temas_por_error_desc() para reportes grupales
    - Crear ordenar_simulacros_desc() por fecha
    - _Requisitos: 3.2, 7.2, 4.1_
  
  - [ ]* 5.4 Escribir pruebas de propiedades para ordenamiento
    - **Propiedad 8: Ordenamiento de temas en clasificación de errores y orientación**
    - **Valida: Requisitos 3.2, 6.1**
    - **Propiedad 9: Identificación correcta del último simulacro**
    - **Valida: Requisitos 4.1, 8.6**

- [ ] 6. Implementar generadores de reportes
  - [ ] 6.1 Crear generador de reporte individual
    - Implementar generar_reporte_individual() con todos los campos requeridos
    - Manejar casos especiales (estudiante sin simulacros, datos incompletos)
    - _Requisitos: 4.2, 4.5_
  
  - [ ]* 6.2 Escribir pruebas de propiedades para reportes individuales
    - **Propiedad 10: Completitud del Reporte Individual**
    - **Valida: Requisitos 4.2, 8.2**
  
  - [ ] 6.3 Crear generador de reporte grupal
    - Implementar generar_reporte_grupal() con agregación correcta
    - Validar acceso del docente a sus grupos asignados
    - _Requisitos: 7.1, 7.3, 8.1_
  
  - [ ]* 6.4 Escribir pruebas de propiedades para reportes grupales
    - **Propiedad 12: Agregación correcta del Reporte Grupal**
    - **Valida: Requisitos 7.1, 7.2, 7.3**
  
  - [ ] 6.5 Crear generador de resumen institucional
    - Implementar generar_resumen_institucional() solo con datos agregados
    - Garantizar que no se exponen datos individuales de estudiantes
    - _Requisitos: 9.1, 9.2, 9.4_
  
  - [ ]* 6.6 Escribir pruebas de propiedades para resumen institucional
    - **Propiedad 13: Agregación correcta del Resumen Institucional sin datos individuales**
    - **Valida: Requisitos 9.1, 9.2, 9.4, 11.5**

- [ ] 7. Checkpoint - Verificar lógica de negocio
  - Asegurar que todas las pruebas pasan, preguntar al usuario si surgen dudas.

- [ ] 8. Implementar módulo NLU con Gemini API
  - [ ] 8.1 Crear cliente Gemini API
    - Implementar wrapper HTTP para Gemini con timeout de 8 segundos
    - Leer GEMINI_API_KEY desde variables de entorno
    - Manejar errores de timeout y códigos HTTP
    - _Requisitos: 10.1, 10.2, 10.3, 10.4_
  
  - [ ] 8.2 Implementar clasificador de intenciones
    - Crear función clasificar_intencion() con catálogo por rol
    - Definir enum Intencion con todas las categorías
    - Restringir datos enviados solo a texto y rol
    - _Requisitos: 10.1, 10.5, 10.6_
  
  - [ ]* 8.3 Escribir pruebas de propiedades para NLU
    - **Propiedad 14: Orden de llamadas en consultas en lenguaje natural**
    - **Valida: Requisitos 10.1, 10.6**
    - **Propiedad 15: Manejo de errores de la Gemini API**
    - **Valida: Requisitos 10.3, 10.4**

- [ ] 9. Implementar módulo de auditoría y logging
  - [ ] 9.1 Crear sistema de logging estructurado
    - Implementar registrar_consulta() con formato JSON
    - Crear registrar_intento_escritura() para operaciones rechazadas
    - Configurar rotación de logs y retención
    - _Requisitos: 11.3, 11.4_
  
  - [ ]* 9.2 Escribir pruebas de propiedades para auditoría
    - **Propiedad 16: Solo lectura del Servidor MCP**
    - **Valida: Requisitos 11.2, 11.4**
    - **Propiedad 17: Registro de auditoría completo y sin contenido de resultados**
    - **Valida: Requisitos 11.3**

- [ ] 10. Implementar API REST con FastAPI
  - [ ] 10.1 Crear router de autenticación
    - Implementar POST /auth/login con validación de credenciales
    - Configurar middleware de CORS y validación JWT
    - Crear dependencies de FastAPI para roles
    - _Requisitos: 1.1, 1.2, 1.3_
  
  - [ ] 10.2 Implementar routers por rol - Estudiante
    - Crear GET /estudiante/reporte para reporte individual
    - Implementar GET /estudiante/comparacion para comparación entre simulacros
    - Crear GET /estudiante/orientacion para orientación de refuerzo
    - _Requisitos: 4.1, 4.2, 5.1, 6.1_
  
  - [ ] 10.3 Implementar routers por rol - Docente
    - Crear GET /docente/reporte-grupal con filtros por simulacro
    - Implementar GET /docente/estudiante/{id} con validación de grupo
    - _Requisitos: 7.1, 8.1, 8.3_
  
  - [ ] 10.4 Implementar routers por rol - Dirección
    - Crear GET /direccion/resumen solo con datos agregados
    - Validar que no se exponen datos individuales
    - _Requisitos: 9.1, 9.2, 9.3_
  
  - [ ] 10.5 Implementar router de chat para lenguaje natural
    - Crear POST /chat con integración Gemini + MCP
    - Validar orden de llamadas (Gemini primero, MCP después)
    - _Requisitos: 10.1, 10.6_
  
  - [ ]* 10.6 Escribir pruebas de integración para API
    - Probar flujos completos por rol con TestClient
    - Validar manejo de errores y timeouts
    - Verificar control de acceso en endpoints

- [ ] 11. Checkpoint - Verificar API completa
  - Asegurar que todas las pruebas pasan, preguntar al usuario si surgen dudas.

- [ ] 12. Implementar frontend HTML + JavaScript
  - [ ] 12.1 Crear páginas HTML base
    - Implementar index.html con formulario de login
    - Crear dashboards por rol: estudiante.html, docente.html, direccion.html
    - Añadir CSS básico y responsive
    - _Requisitos: 1.1, 4.1, 7.1, 9.1_
  
  - [ ] 12.2 Implementar lógica JavaScript de autenticación
    - Crear auth.js con manejo de JWT en sessionStorage
    - Implementar redirección automática según rol
    - Manejar expiración de tokens
    - _Requisitos: 1.3, 1.4_
  
  - [ ] 12.3 Implementar interfaz del estudiante
    - Crear estudiante.js con consultas de reporte individual
    - Implementar comparación entre simulacros
    - Añadir interfaz de chat en lenguaje natural
    - _Requisitos: 4.1, 5.1, 6.1, 10.1_
  
  - [ ] 12.4 Implementar interfaz del docente
    - Crear docente.js con reportes grupales
    - Implementar vista de detalle de estudiantes
    - Añadir filtros por simulacro y grupo
    - _Requisitos: 7.1, 8.1, 8.6_
  
  - [ ] 12.5 Implementar interfaz de la dirección
    - Crear direccion.js solo con datos agregados
    - Implementar resumen institucional por simulacro
    - Validar que no se muestran datos individuales
    - _Requisitos: 9.1, 9.2, 9.4_

- [ ] 13. Crear base de datos SQLite con datos simulados
  - [x] 13.1 Crear esquema de base de datos
    - Implementar schema.sql con todas las tablas requeridas
    - Definir relaciones y restricciones de integridad
    - _Requisitos: 11.1_
  
  - [ ] 13.2 Generar datos simulados
    - Crear seed_simulados.py con datos ficticios del CNI
    - Generar usuarios, grupos, simulacros y respuestas simuladas
    - Validar que no se usan datos reales de estudiantes
    - _Requisitos: 11.1, 11.5_

- [ ] 14. Configuración del entorno y documentación
  - [ ] 14.1 Crear configuración de desarrollo
    - Implementar config.py con lectura de variables de entorno
    - Crear .env.example con todas las variables necesarias
    - Configurar main.py como punto de entrada de FastAPI
    - _Requisitos: 10.2_
  
  - [ ] 14.2 Escribir documentación del proyecto
    - Actualizar README.md con instrucciones de instalación y uso
    - Documentar configuración del servidor MCP de la semana 4
    - Crear guía de desarrollo y testing
    - _Requisitos: General_

- [ ] 15. Checkpoint final y pruebas de integración completa
  - [ ] 15.1 Ejecutar suite completa de pruebas
    - Verificar todas las pruebas unitarias y de propiedades
    - Ejecutar pruebas de integración con mocks
    - Validar cobertura de código mínima (85%)
    - _Requisitos: Todos_
  
  - [ ]* 15.2 Pruebas de humo y seguridad
    - Verificar que GEMINI_API_KEY no aparece en código
    - Validar que solo se usan datos simulados
    - Comprobar que MCP está en modo solo lectura
    - _Requisitos: 10.2, 11.1, 11.2_
  
  - [ ] 15.3 Integración final con servidor MCP
    - Configurar conexión con el servidor MCP de la semana 4
    - Verificar que todas las consultas funcionan correctamente
    - Probar manejo de errores y timeouts del MCP
    - _Requisitos: 2.2, 2.3_

## Notes

- Las tareas marcadas con `*` son opcionales y pueden omitirse para un MVP más rápido
- Cada tarea referencia los requisitos específicos para trazabilidad
- Los checkpoints aseguran validación incremental del progreso
- Las pruebas de propiedades validan las garantías de corrección universales
- Las pruebas unitarias validan ejemplos específicos y casos borde
- Todas las implementaciones siguen la arquitectura definida en el documento de diseño
- El sistema usa exclusivamente datos simulados en cumplimiento de la Ley N.º 29733
- La integración con el servidor MCP de la semana 4 es esencial para el funcionamiento

## Task Dependency Graph

```json
{
  "waves": [
    { "id": 0, "tasks": ["1"] },
    { "id": 1, "tasks": ["2.1", "4.1", "13.1"] },
    { "id": 2, "tasks": ["2.3", "4.2", "13.2", "9.1", "14.1"] },
    { "id": 3, "tasks": ["2.2", "2.4", "4.3", "5.1"] },
    { "id": 4, "tasks": ["5.2", "5.3", "8.1"] },
    { "id": 5, "tasks": ["5.4", "6.1", "8.2"] },
    { "id": 6, "tasks": ["6.2", "6.3", "8.3", "9.2"] },
    { "id": 7, "tasks": ["6.4", "6.5", "10.1"] },
    { "id": 8, "tasks": ["6.6", "10.2", "10.3", "10.4"] },
    { "id": 9, "tasks": ["10.5", "12.1"] },
    { "id": 10, "tasks": ["10.6", "12.2", "12.3", "12.4", "12.5"] },
    { "id": 11, "tasks": ["14.2"] },
    { "id": 12, "tasks": ["15.1"] },
    { "id": 13, "tasks": ["15.2", "15.3"] }
  ]
}
```