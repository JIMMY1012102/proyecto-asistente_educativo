# Drivers arquitectónicos v1

## 1. Funcionalidad núcleo

| ID | Driver | Por qué condiciona la arquitectura |
|---|---|---|
| R1 | Autenticación y control de acceso por rol | Todas las funciones dependen de identidad, sesión y permisos. |
| R2 | Procesamiento automático de respuestas | El sistema debe obtener y procesar datos de simulacros de forma controlada. |
| R3 | Clasificación de errores por tema y estudiante | Define la lógica central de cálculo y retroalimentación. |
| R10 | Consultas en lenguaje natural | Introduce dependencia de un servicio externo de interpretación y manejo de fallos. |
| R11 | Protección de datos | Condiciona acceso, auditoría, anonimización y tratamiento de información. |

## 2. Atributos de calidad

| Atributo | Escenario medible | Prioridad | Traza |
|---|---|---|---|
| Rendimiento | Las operaciones individuales deben responder en menos de 5 segundos y el procesamiento de datos en los límites indicados por cada requisito. | Alta | R1, R2, R3 |
| Seguridad | Ningún usuario debe acceder a información fuera de su rol y ningún dato personal real debe ser procesado. | Alta | R1, R11 |
| Disponibilidad | [INFERIDO] Ante la caída de un servicio externo, el sistema debe informar el fallo sin exponer datos ni generar resultados parciales. | Media | R2, R10 |

## 3. Restricciones

| Restricción | Decisión que condiciona |
|---|---|
| Solo se utilizarán datos simulados. | Impide almacenar o procesar datos personales reales durante desarrollo y demostración. |
| El acceso a los datos será exclusivamente de solo lectura. | Impide operaciones de modificación o eliminación desde la aplicación. |
| Los secretos no pueden almacenarse en código ni archivos versionados. | Obliga a mantener credenciales fuera del repositorio. |
| No se enviarán resultados ni identificadores de estudiantes a servicios externos. | Limita la información compartida fuera del sistema. |

## 4. Riesgos arquitectónicos

| Riesgo | Indicador temprano | Consecuencia |
|---|---|---|
| El servicio externo de interpretación no responde dentro del tiempo permitido. | Respuestas superiores a 8 segundos o errores repetidos. | Revisar la dependencia del servicio para las consultas. |
| El servicio de acceso a datos no responde dentro del tiempo permitido. | Errores o tiempos de espera durante las consultas. | Revisar el flujo de procesamiento y recuperación ante fallos. |
| Un rol accede a datos que no le corresponden. | Prueba de autorización permite visualizar información restringida. | Rediseñar control de acceso y autorización. |

## 5. Diferencias con la ficha manual

La ficha manual identificó R1, R2, R3, R10 y R11 como historias/requisitos críticos, y Rendimiento, Seguridad y Disponibilidad como atributos principales.

La revisión asistida añadió escenarios medibles, restricciones y riesgos con indicadores tempranos.

## Decisiones que la arquitectura NO debe tomar esta semana

- Implementación del agente conversacional.
- Implementación de la conexión prevista para la Unidad 3.
- Detalles visuales finales de la interfaz.
- Optimizaciones prematuras no justificadas por requisitos.
