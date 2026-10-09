# Stack y reglas técnicas

- Framework: CodeIgniter 4, versión estable vigente [VERIFICAR].
- Arquitectura: monolito MVC en capas con renderizado en servidor.
- Base de datos: MySQL/MariaDB de XAMPP; collation utf8mb4_unicode_ci.
- Servidor: Apache de XAMPP; raíz pública: public/.
- Nombres: español; snake_case en base de datos; PascalCase en clases; kebab-case en rutas.
- Secretos únicamente en .env; .env nunca se versiona.
- Todo módulo nuevo debe trazar a una historia de requirements.md; si no traza, no se construye.
- FRONTERA: no implementar agente conversacional, modelos de IA ni MCP hasta la Unidad 3.
- Dejar únicamente el punto de extensión documentado.

## Referencias arquitectónicas

- docs/arquitectura/drivers.md
- docs/adr/ADR-001.md
- docs/adr/ADR-002.md
- docs/adr/ADR-003.md

- Toda tabla nueva obliga a actualizar docs/arquitectura/modelo_datos.md en el mismo commit.
