# Requirements Document

## Introduction

El **Asistente de Retroalimentación para Simulacros de Admisión del CNI** es una aplicación web que automatiza el procesamiento y la clasificación de los resultados de los simulacros de admisión del Colegio Nacional de Ica (CNI). El sistema permite a los estudiantes de 5.º de secundaria consultar sus errores por tema y conocer su evolución entre simulacros; a los docentes, revisar el rendimiento de su grupo y de estudiantes individuales; y a la dirección de la institución, acceder a un resumen agregado por nivel. Todo acceso a la base de datos se realiza exclusivamente a través del servidor MCP de solo lectura construido en la semana 4, y todos los datos empleados durante el desarrollo son simulados en cumplimiento de la Ley N.º 29733 de Protección de Datos Personales.

---

## Glossary

- **Asistente**: Sistema web desarrollado en FastAPI que recibe consultas en lenguaje natural o por interfaz gráfica, las procesa con apoyo de la Gemini API y responde con información de retroalimentación.
- **Servidor_MCP**: Servidor MCP de solo lectura construido en la semana 4, único punto de acceso autorizado a la base de datos SQLite de resultados.
- **Base_de_Datos**: Base de datos SQLite que contiene datos simulados de estudiantes, simulacros, respuestas y temas.
- **Estudiante**: Usuario de 5.º de secundaria del CNI que consulta sus propios resultados y retroalimentación.
- **Docente**: Usuario autenticado que consulta resultados de los estudiantes de sus grupos asignados.
- **Dirección**: Usuario autenticado que pertenece a la dirección de la institución y solo accede a datos agregados por nivel.
- **Simulacro**: Prueba de admisión aplicada al grupo de 5.º de secundaria del CNI en una fecha determinada.
- **Reporte_Individual**: Documento de retroalimentación personalizado generado para un estudiante específico respecto a un simulacro.
- **Reporte_Grupal**: Documento de retroalimentación agregado generado para el grupo completo de un docente respecto a un simulacro.
- **Resumen_Institucional**: Vista agregada de resultados por tema a nivel de todos los grupos de 5.º de secundaria, accesible únicamente para la Dirección.
- **Tema**: Área del conocimiento evaluada en el simulacro (p. ej., Matemáticas, Comprensión Lectora, Ciencias).
- **Porcentaje_de_Aciertos**: Cociente entre las respuestas correctas y el total de preguntas de un tema, expresado en porcentaje entero.
- **Variación_de_Puntaje**: Diferencia absoluta y relativa entre el puntaje de un simulacro y el inmediatamente anterior para el mismo estudiante y tema.
- **Gemini_API**: API de Google utilizada para interpretar consultas en lenguaje natural y generar respuestas de retroalimentación; la clave de acceso se almacena únicamente en variables de entorno.
- **Autenticador**: Módulo del Asistente responsable de verificar la identidad y el rol del usuario antes de conceder acceso a cualquier funcionalidad.

---

## Requirements

### Requisito 1: Autenticación y control de acceso por rol

**Historia de usuario:** Como usuario del sistema, quiero iniciar sesión con mis credenciales y que el sistema reconozca mi rol, para que solo pueda acceder a las funcionalidades correspondientes a mi perfil.

#### Criterios de aceptación

1. WHEN un usuario envía credenciales válidas (nombre de usuario y contraseña no vacíos), THE Autenticador SHALL verificar la identidad del usuario y asignarle el rol correspondiente (Estudiante, Docente o Dirección) en un tiempo menor a 2 segundos desde la recepción de la solicitud.
2. IF un usuario envía credenciales inválidas (usuario no registrado, contraseña incorrecta) o ausentes (campos vacíos o nulos), THEN THE Autenticador SHALL rechazar el acceso y devolver un mensaje de error genérico que indique que las credenciales son incorrectas, sin revelar qué campo específico es incorrecto.
3. WHILE un usuario mantiene una sesión activa, THE Autenticador SHALL validar el token de sesión en cada solicitud antes de permitir el acceso a cualquier recurso protegido del sistema.
4. IF el token de sesión de un usuario ha superado 8 horas desde su emisión o contiene una firma inválida, THEN THE Autenticador SHALL rechazar la solicitud, devolver al usuario un mensaje que indique que la sesión ha expirado y redirigirlo al formulario de inicio de sesión.
5. IF un Estudiante autenticado intenta acceder a los datos de otro Estudiante, a los reportes grupales del Docente o al Resumen_Institucional de la Dirección, THEN THE Autenticador SHALL rechazar la solicitud y devolver un mensaje de acceso no autorizado indicando que el recurso no está disponible para su rol.
6. IF un Docente autenticado intenta acceder a los datos individuales de un Estudiante que no pertenece a ninguno de sus grupos asignados, THEN THE Autenticador SHALL rechazar la solicitud y devolver un mensaje de acceso no autorizado indicando que el Estudiante no pertenece a sus grupos.
7. IF un usuario con rol Dirección intenta acceder al detalle individual de cualquier Estudiante, THEN THE Autenticador SHALL rechazar la solicitud y devolver un mensaje de acceso no autorizado indicando que la Dirección solo puede acceder a datos agregados.

---

### Requisito 2: Procesamiento automático de respuestas del simulacro

**Historia de usuario:** Como docente, quiero que el sistema procese automáticamente las respuestas de cada simulacro consultando la base de datos, para no tener que clasificarlas manualmente.

#### Criterios de aceptación

1. WHEN el Asistente recibe una solicitud de procesamiento para un simulacro identificado por su identificador único, THE Servidor_MCP SHALL devolver las respuestas de todos los Estudiantes con registros en ese simulacro en un tiempo menor a 5 segundos desde la recepción de la solicitud.
2. THE Asistente SHALL consultar los resultados del simulacro exclusivamente a través del Servidor_MCP; el Asistente no SHALL establecer ninguna conexión directa con la Base_de_Datos.
3. IF el Servidor_MCP no devuelve una respuesta en 10 segundos o devuelve un código de error HTTP, THEN THE Asistente SHALL registrar el evento en el log del sistema con marca de tiempo y código de error, y SHALL devolver al usuario un mensaje que indique que el servicio de datos no está disponible temporalmente.
4. IF el identificador de simulacro proporcionado en la solicitud no corresponde a ningún registro en la Base_de_Datos, THEN THE Asistente SHALL devolver al usuario un mensaje indicando que el simulacro solicitado no existe y no generará ningún resultado parcial.
5. IF los datos de respuesta de un Estudiante para un simulacro están incompletos (campos obligatorios nulos o ausentes) o contienen valores fuera del dominio permitido, THEN THE Asistente SHALL omitir ese registro del procesamiento, registrar la inconsistencia en el log del sistema e informar al usuario del número de registros omitidos al finalizar el procesamiento.

---

### Requisito 3: Clasificación de errores por tema y por estudiante

**Historia de usuario:** Como docente, quiero que el sistema clasifique los errores de cada estudiante por tema, para identificar rápidamente las áreas de menor desempeño en el grupo.

#### Criterios de aceptación

1. WHEN el Asistente completa el procesamiento de un simulacro, THE Asistente SHALL calcular el Porcentaje_de_Aciertos por Tema para cada Estudiante que participó, aplicando la fórmula: (número de respuestas correctas del Estudiante en el Tema ÷ número total de preguntas del Tema en ese simulacro) × 100, expresado con un decimal de precisión en el rango 0.0–100.0.
2. WHEN el Asistente presenta los resultados de clasificación de errores a cualquier usuario, THE Asistente SHALL ordenar los Temas de menor a mayor Porcentaje_de_Aciertos del Estudiante o del grupo, según corresponda al tipo de reporte solicitado.
3. IF un Tema no tiene preguntas registradas en un simulacro, THEN THE Asistente SHALL excluir ese Tema del reporte de clasificación para ese simulacro e informar al Docente o al Estudiante solicitante cuántos Temas fueron excluidos por ese motivo.
4. WHILE el Asistente procesa la clasificación de errores de un simulacro, THE Asistente SHALL asociar cada error clasificado al identificador único del Estudiante, al identificador del Simulacro y al identificador del Tema, sin almacenar esos datos en ningún almacenamiento persistente fuera de la sesión activa del usuario.
5. IF un Estudiante no registró ninguna respuesta para un Tema determinado en un simulacro, THEN THE Asistente SHALL asignar un Porcentaje_de_Aciertos de 0.0 % para ese Tema e incluir al Estudiante en el reporte de clasificación con ese valor.

---

### Requisito 4: Reporte individual de retroalimentación del estudiante

**Historia de usuario:** Como estudiante, quiero consultar en qué temas cometí errores en mi último simulacro, para saber qué debo reforzar.

#### Criterios de aceptación

1. WHEN un Estudiante autenticado solicita su Reporte_Individual, THE Asistente SHALL identificar como "último simulacro" el simulacro con la fecha de aplicación más reciente registrada para ese Estudiante y SHALL devolver la lista de Temas donde el Estudiante registró al menos una respuesta incorrecta, junto con el Porcentaje_de_Aciertos por Tema, en un tiempo menor a 5 segundos desde la recepción de la solicitud.
2. WHEN el Asistente genera el Reporte_Individual, THE Asistente SHALL incluir el nombre del Simulacro, la fecha de aplicación, el puntaje total del Estudiante expresado como número de respuestas correctas sobre el total de preguntas, y el Porcentaje_de_Aciertos global.
3. WHEN un Estudiante formula la consulta «¿en qué temas fallé?» u otras expresiones equivalentes en lenguaje natural, THE Gemini_API SHALL clasificar la intención de la consulta y devolver la categoría de intención al Asistente; THEN THE Asistente SHALL responder con el contenido del Reporte_Individual del último simulacro registrado para ese Estudiante.
4. IF la Gemini_API no puede clasificar la intención de la consulta del Estudiante, THEN THE Asistente SHALL informar al Estudiante que la consulta no fue reconocida y SHALL listar los tipos de consulta disponibles para su rol.
5. IF el Estudiante no tiene ningún simulacro registrado en la Base_de_Datos, THEN THE Asistente SHALL informar al Estudiante que no existen resultados disponibles para su cuenta, sin generar un reporte vacío ni ejecutar consultas adicionales al Servidor_MCP.
6. IF un Estudiante autenticado intenta consultar el Reporte_Individual de otro Estudiante, THEN THE Asistente SHALL rechazar la solicitud y devolver un mensaje de acceso no autorizado, sin revelar datos del Estudiante consultado.

---

### Requisito 5: Comparación de desempeño entre simulacros del estudiante

**Historia de usuario:** Como estudiante, quiero conocer mi puntaje y comparación con simulacros anteriores, para saber si estoy mejorando.

#### Criterios de aceptación

1. WHEN un Estudiante autenticado con al menos dos simulacros registrados solicita su comparación de desempeño, THE Asistente SHALL calcular la Variación_de_Puntaje por Tema como (puntaje_simulacro_más_reciente − puntaje_simulacro_inmediatamente_anterior) en puntos absolutos por Tema, donde los simulacros se ordenan cronológicamente por fecha de registro descendente, y SHALL mostrar el resultado citando la fecha de aplicación de cada simulacro en un tiempo menor a 5 segundos.
2. WHEN el Asistente muestra la comparación de desempeño, THE Asistente SHALL etiquetar cada Tema con «Mejora» si la Variación_de_Puntaje es mayor a cero, «Retroceso» si es menor a cero, o «Sin cambio» si es igual a cero.
3. WHEN un Estudiante formula la consulta «¿cómo voy comparado con el simulacro anterior?» u otras expresiones equivalentes en lenguaje natural, THE Gemini_API SHALL clasificar la intención de la consulta y devolver la categoría de intención al Asistente.
4. WHEN la Gemini_API devuelve la categoría de intención de comparación de desempeño, THE Asistente SHALL responder con la Variación_de_Puntaje por Tema entre los dos últimos simulacros registrados para ese Estudiante.
5. IF la Gemini_API no puede clasificar la intención de la consulta del Estudiante, THEN THE Asistente SHALL informar al Estudiante que la consulta no fue reconocida y SHALL listar los tipos de consulta disponibles para su rol.
6. IF un Estudiante tiene registrado un único simulacro, THEN THE Asistente SHALL informar que no existen simulacros anteriores con los cuales comparar y SHALL mostrar únicamente los resultados del simulacro disponible.
7. IF un Estudiante no tiene ningún simulacro registrado, THEN THE Asistente SHALL informar que no existen resultados disponibles para generar una comparación.

---

### Requisito 6: Orientación de refuerzo por temas con menor desempeño

**Historia de usuario:** Como estudiante, quiero recibir orientación sobre qué temas reforzar según mis errores, para no depender exclusivamente del docente para decidir qué estudiar.

#### Criterios de aceptación

1. WHEN un Estudiante autenticado solicita orientación de refuerzo, THE Asistente SHALL presentar la lista de Temas del último simulacro ordenados de menor a mayor Porcentaje_de_Aciertos; en caso de empate en Porcentaje_de_Aciertos, los Temas SHALL ordenarse de mayor a menor número de respuestas incorrectas.
2. WHEN un Estudiante formula la solicitud de orientación en lenguaje natural y la Gemini_API devuelve la categoría de intención de orientación de refuerzo, THE Asistente SHALL responder con los Temas priorizados según el Porcentaje_de_Aciertos del último simulacro registrado para ese Estudiante.
3. IF la Gemini_API devuelve una intención de orientación de refuerzo no reconocida o ambigua, THEN THE Asistente SHALL informar al Estudiante que la consulta no fue reconocida y SHALL listar los tipos de consulta disponibles para su rol.
4. IF el historial de simulacros del Estudiante no contiene ningún simulacro donde todas las preguntas de todos los Temas tengan una respuesta registrada y un Porcentaje_de_Aciertos calculado, THEN THE Asistente SHALL declarar explícitamente que no se encontró suficiente información para generar orientación de refuerzo.
5. THE Asistente SHALL limitar la orientación de refuerzo a la priorización de Temas según los datos de simulacros disponibles; THE Asistente no SHALL generar recomendaciones de material de estudio, rutas de aprendizaje personalizadas ni contenido externo de ningún tipo.

---

### Requisito 7: Reporte grupal de errores por tema para el docente

**Historia de usuario:** Como docente, quiero ver la clasificación de errores de todo mi grupo por tema, para anticipar qué reforzar en clase antes del próximo simulacro.

#### Criterios de aceptación

1. WHEN un Docente autenticado solicita el Reporte_Grupal de su grupo para un simulacro identificado, THE Asistente SHALL calcular el porcentaje de error por Tema agregando las respuestas incorrectas de todos los Estudiantes del grupo inscritos en ese simulacro y SHALL devolver el resultado en un tiempo menor a 10 segundos desde la recepción de la solicitud.
2. WHEN el Asistente genera el Reporte_Grupal, THE Asistente SHALL ordenar los Temas de mayor a menor porcentaje de error para facilitar la identificación de las áreas de mayor debilidad del grupo.
3. WHEN el Asistente genera el Reporte_Grupal, THE Asistente SHALL incluir el nombre del grupo, el nombre del Simulacro, la fecha de aplicación y el número total de Estudiantes cuyos datos fueron incluidos en el cálculo.
4. IF el grupo del Docente no tiene Estudiantes con resultados registrados para el simulacro solicitado, THEN THE Asistente SHALL informar al Docente que no existen resultados disponibles para ese grupo en ese simulacro y no generará un reporte vacío.
5. WHEN un Docente autenticado solicita filtrar el Reporte_Grupal por un simulacro específico, THE Asistente SHALL presentar primero la lista de simulacros disponibles para el grupo y SHALL generar el Reporte_Grupal únicamente para el simulacro que el Docente seleccione de esa lista.

---

### Requisito 8: Detalle individual de un estudiante del grupo (vista docente)

**Historia de usuario:** Como docente, quiero consultar el detalle de un estudiante específico de mi grupo, para anticipar observaciones antes de una tutoría individual.

#### Criterios de aceptación

1. WHEN un Docente autenticado solicita el detalle de un Estudiante que pertenece a uno de sus grupos asignados, THE Asistente SHALL mostrar los errores por Tema y la Variación_de_Puntaje (definida como la diferencia entre el puntaje del simulacro más reciente y el inmediatamente anterior para ese Estudiante) en un tiempo menor a 5 segundos desde la recepción de la solicitud.
2. WHEN el Asistente muestra el detalle del Estudiante, THE Asistente SHALL incluir el identificador anonimizado del Estudiante (según lo definido en la Base_de_Datos de datos simulados), el identificador del simulacro más reciente y la fecha de aplicación de ese simulacro.
3. IF el Docente solicita el detalle de un Estudiante que no pertenece a ninguno de sus grupos asignados, THEN THE Asistente SHALL rechazar la solicitud y devolver un mensaje de acceso no autorizado indicando que el Estudiante no pertenece a sus grupos.
4. IF el Estudiante consultado no tiene simulacros registrados en la Base_de_Datos, THEN THE Asistente SHALL informar al Docente que no existen resultados disponibles para ese Estudiante.
5. IF el Servidor_MCP no devuelve una respuesta en 5 segundos al consultar el detalle del Estudiante, THEN THE Asistente SHALL informar al Docente que el servicio de datos no está disponible temporalmente y registrará el evento en el log del sistema.
6. WHEN un Docente autenticado solicita navegar entre los simulacros de un Estudiante y ese Estudiante tiene más de un simulacro registrado, THE Asistente SHALL presentar los simulacros disponibles ordenados cronológicamente de más reciente a más antiguo y SHALL mostrar los resultados del simulacro que el Docente seleccione.

---

### Requisito 9: Resumen agregado por nivel para la dirección institucional

**Historia de usuario:** Como parte directiva de la institución, quiero ver el estado agregado de resultados de todos los grupos de 5.º de secundaria, para anticipar qué temas requieren refuerzo a nivel institucional.

#### Criterios de aceptación

1. WHEN un usuario de la Dirección autenticado solicita el Resumen_Institucional para un simulacro seleccionado, THE Asistente SHALL calcular el porcentaje de error por Tema como (número total de respuestas incorrectas en el Tema ÷ número total de respuestas en el Tema) × 100, redondeado a 2 decimales, agregando los datos de todos los grupos de 5.º de secundaria con resultados registrados para ese simulacro, y SHALL devolver el resultado en un tiempo menor a 15 segundos.
2. THE Resumen_Institucional SHALL mostrar únicamente datos agregados por Tema y por grupo; el Asistente no SHALL exponer identificadores de Estudiantes ni datos desagregados a nivel individual en ninguna vista accesible al rol Dirección.
3. IF un usuario con rol Dirección intenta acceder al detalle individual de un Estudiante, THEN THE Asistente SHALL rechazar la solicitud y devolver un mensaje de acceso no autorizado indicando que la Dirección solo puede acceder a datos agregados.
4. WHEN el Asistente genera el Resumen_Institucional, THE Asistente SHALL incluir el nombre del Simulacro, la fecha de aplicación, el número total de grupos incluidos en el cálculo y el número total de Estudiantes incluidos en el cálculo.
5. IF no existen simulacros con resultados registrados para ningún grupo de 5.º de secundaria en la Base_de_Datos, THEN THE Asistente SHALL informar a la Dirección que no existen resultados disponibles para generar el Resumen_Institucional, mostrando un mensaje descriptivo.
6. IF solo algunos grupos de 5.º de secundaria tienen resultados registrados para el simulacro seleccionado, THEN THE Asistente SHALL incluir únicamente los grupos con datos disponibles en el cálculo y SHALL indicar en el Resumen_Institucional cuántos grupos fueron excluidos por falta de resultados.
7. WHEN un usuario de la Dirección autenticado accede al Resumen_Institucional, THE Asistente SHALL presentar la lista de simulacros disponibles para 5.º de secundaria y SHALL generar el Resumen_Institucional únicamente para el simulacro que la Dirección seleccione de esa lista.

---

### Requisito 10: Integración con la Gemini API para consultas en lenguaje natural

**Historia de usuario:** Como usuario del sistema, quiero formular mis consultas en lenguaje natural en español, para interactuar con el asistente sin necesidad de aprender comandos específicos.

#### Criterios de aceptación

1. WHEN un usuario envía una consulta en lenguaje natural, THE Asistente SHALL enviar la consulta textual a la Gemini_API para su clasificación de intención antes de ejecutar cualquier consulta al Servidor_MCP.
2. THE Asistente SHALL leer la clave de acceso a la Gemini_API exclusivamente desde una variable de entorno del sistema en tiempo de ejecución; la clave no SHALL aparecer en el código fuente, en archivos de configuración ni en ningún archivo versionado en el repositorio.
3. IF la Gemini_API no responde en 8 segundos desde el envío de la consulta, THEN THE Asistente SHALL cancelar la solicitud, preservar el texto de la consulta del usuario y devolver un mensaje que indique que el servicio de interpretación no está disponible temporalmente.
4. IF la Gemini_API devuelve un código de error HTTP, THEN THE Asistente SHALL registrar el error en el log del sistema con marca de tiempo y código de respuesta, y SHALL devolver al usuario un mensaje que indique que el servicio de interpretación no está disponible e invitará al usuario a usar la navegación por menús.
5. WHEN la Gemini_API devuelve una intención de consulta no reconocida o fuera del catálogo de funcionalidades del sistema, THE Asistente SHALL informar al usuario que la consulta no puede ser procesada y SHALL listar los tipos de consultas disponibles según el rol activo del usuario.
6. THE Asistente SHALL restringir los datos enviados a la Gemini_API al texto de la consulta del usuario y la etiqueta del rol activo; THE Asistente no SHALL enviar identificadores de Estudiantes, resultados de simulacros ni ningún otro dato derivado de la Base_de_Datos a la Gemini_API.

---

### Requisito 11: Protección de datos y cumplimiento de la Ley N.º 29733

**Historia de usuario:** Como institución educativa, quiero que el sistema cumpla con la Ley N.º 29733 de Protección de Datos Personales, para garantizar la privacidad de los estudiantes menores de edad durante el desarrollo y la operación del sistema.

#### Criterios de aceptación

1. THE Asistente SHALL utilizar exclusivamente datos simulados en todos los entornos del sistema (desarrollo, pruebas y demostración); ningún dato personal real de Estudiantes SHALL ser almacenado, procesado ni transmitido por el sistema en ningún entorno.
2. THE Servidor_MCP SHALL estar configurado para aceptar únicamente operaciones de lectura (SELECT); el Asistente no SHALL disponer de credenciales ni permisos para ejecutar operaciones de escritura, modificación o eliminación sobre la Base_de_Datos en ningún entorno.
3. WHEN el Asistente ejecuta cualquier consulta que accede a datos de Estudiantes a través del Servidor_MCP, THE Asistente SHALL registrar en el log del sistema el identificador del usuario solicitante, el rol activo, el tipo de consulta y la marca de tiempo, sin registrar el contenido de los resultados individuales devueltos.
4. IF un usuario intenta ejecutar una operación de escritura o modificación sobre la Base_de_Datos a través del Servidor_MCP, THEN THE Servidor_MCP SHALL rechazar la operación, devolver un mensaje de error al Asistente indicando que la operación no está permitida, y THE Asistente SHALL registrar el intento en el log del sistema con el identificador del usuario y la marca de tiempo.
5. THE Asistente SHALL presentar todos los datos de Estudiantes en cualquier vista del sistema utilizando únicamente el identificador anonimizado definido en la Base_de_Datos de datos simulados; el Asistente no SHALL exponer nombres reales, documentos de identidad ni ningún otro atributo personal identificable en ninguna vista ni en ningún entorno.
