# Respuesta a la objeción 1 del acta de auditoría

## (a) Reformulación

La especificación heredada contiene decisiones tecnológicas anteriores que no coinciden con la arquitectura definida para la sesión 6.

## (b) Aceptación o refutación

**Aceptamos la objeción.**

La inconsistencia es visible entre `requirements.md` y los ADR. Además, `docs/arquitectura/modelo_datos.md` ya advierte que algunos requisitos describen SQLite/FastAPI/MCP mientras la arquitectura de la sesión utiliza MariaDB/MySQL sobre XAMPP.

## (c) Decisión final

Se mantienen ADR-001 y ADR-002 para la sesión 6.

Antes de comenzar la implementación de la semana 7 se deberá armonizar la especificación para evitar que dos stacks tecnológicos distintos sean considerados simultáneamente fuente de verdad.

No se realiza una edición silenciosa de los ADR porque la objeción no cambia la decisión arquitectónica actual; identifica una inconsistencia documental previa.

## (d) Supuestos no verificados

**[SUPUESTO]** Las restricciones técnicas de la sesión 6 sustituyen las referencias tecnológicas anteriores de la especificación.

**[VERIFICAR]** Confirmar con la docente antes de la semana 7 si `requirements.md` debe actualizarse formalmente.
