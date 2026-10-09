# Producto · Asistente de retroalimentación para simulacros de admisión (CNI)

Redacta todos los documentos en español.

## Propósito
Ayudar a estudiantes de 5.º de secundaria del CNI a conocer sus errores por
tema tras cada simulacro de admisión, y a los docentes a clasificar
automáticamente esos errores por estudiante y por grupo.

## Usuarios
- Estudiante de 5.º de secundaria del CNI
- Docente
- Dirección de la institución

## Lo que hace (funcionalidades DENTRO)
- Procesar automáticamente las respuestas de cada simulacro consultando la
  base de datos mediante el servidor MCP de solo lectura de la semana 4.
- Clasificar los errores por tema y por estudiante.
- Generar el reporte individual de retroalimentación del estudiante.
- Generar el reporte grupal de errores por tema para el docente.
- Comparar el desempeño de un estudiante entre simulacros.
- Mostrar el resumen agregado por nivel para la dirección de la institución.

## Lo que NO hace (FUERA, literal)
- Recomendación automática de material de estudio personalizado (IA
  adaptativa avanzada).
- Integración con plataformas externas de otras academias o simuladores.
- Módulo de comunicación directa docente-apoderado.
- Emisión de notas o resultados oficiales del simulacro.
- Notificaciones automáticas al estudiante o apoderado.
- Escritura o modificación de la base de datos de resultados.

## Reglas no negociables (datos y proceso)
- Reutiliza el servidor MCP construido en la semana 4, en modo exclusivo de
  solo lectura.
- Todos los datos de estudiantes usados en el desarrollo son simulados; no
  se emplea ningún dato personal real (Ley N.° 29733), dado que los
  usuarios reales son menores de edad.
- La dirección de la institución solo accede a datos agregados, nunca al
  detalle individual de un estudiante.
- El asistente no reemplaza el juicio pedagógico del docente ni emite
  calificaciones oficiales.