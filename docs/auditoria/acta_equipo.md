# Acta de auditoría cruzada

**Equipo auditor:** [PENDIENTE EQUIPO AUDITOR]
**Equipo auditado:** Malasquez Laredo Jimmy Alexander · Alvarez Calagua Nia Elizabeth · Rojas Castillo Sebastian Jaren
**Fecha:** 2026-10-09

## Documentos revisados

- docs/adr/ADR-001.md
- docs/adr/ADR-002.md
- docs/adr/ADR-003.md
- docs/arquitectura/c4_contenedores.md
- docs/arquitectura/c4_componentes.md
- docs/arquitectura/modelo_datos.md

## Objeciones entregadas (2)

### Objeción 1

**Enunciado:** Existe una inconsistencia entre la especificación heredada de la semana 5 y la arquitectura definida en la semana 6. `requirements.md` todavía menciona FastAPI, SQLite y acceso mediante MCP, mientras los ADR adoptan CodeIgniter 4, XAMPP y MariaDB/MySQL.

**Dónde se verifica:** `requirements.md`, `ADR-001.md`, `ADR-002.md` y `modelo_datos.md`.

**Evidencia antes de semana 7:** Comparar las tecnologías declaradas en esos documentos.

**Decisión que cambiaría:** Sincronizar `requirements.md` con la arquitectura aprobada o revisar los ADR antes de implementar.

### Objeción 2

**Enunciado:** El requisito de acceso futuro mediante MCP de solo lectura entra en tensión con el componente `Modelo Registro Acceso`, que contempla insertar registros de auditoría en la base de datos.

**Dónde se verifica:** R11, `design.md`, `modelo_datos.md` y `schema.sql`.

**Evidencia antes de semana 7:** Verificar si la auditoría requiere INSERT en la misma base que debe quedar disponible únicamente mediante lectura.

**Decisión que cambiaría:** Mover la auditoría a logs de aplicación o definir explícitamente un mecanismo de persistencia que no contradiga la frontera de solo lectura.

## Objeciones descartadas (3)

1. **Usar SPA en lugar de renderizado en servidor.** Se descarta porque no demuestra incumplimiento de un driver y ADR-001 ya decidió renderizado en servidor.
2. **Cambiar CodeIgniter 4 únicamente porque Laravel tiene más funcionalidades.** Se descarta porque es una comparación genérica y no demuestra una falla concreta del proyecto.
3. **No desplegar en infraestructura productiva esta semana.** Se descarta porque el alcance de la sesión utiliza explícitamente XAMPP como entorno de laboratorio.

## Firmas

**Equipo auditor:** [PENDIENTE]

**Equipo auditado:**
- Malasquez Laredo Jimmy Alexander
- Alvarez Calagua Nia Elizabeth
- Rojas Castillo Sebastian Jaren
