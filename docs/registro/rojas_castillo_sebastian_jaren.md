# Registro individual — Sesión 6

**Estudiante:** Rojas Castillo Sebastian Jaren
**Fecha:** 2026-10-09

## Registro de decisiones

| Actividad | Decisión | Razón / corrección propia |
|---|---|---|
| PL-01 · Drivers | Aceptar con ajustes | Se priorizaron R1, R2, R3, R10 y R11; atributos: rendimiento, seguridad y disponibilidad. |
| PL-02 · Arquitectura y ADR | Aceptar | Se eligió CodeIgniter 4 para evitar construir desde cero la infraestructura MVC. |
| PL-K1 · Diseño en Kiro | Aceptar con revisión | Se verificaron C4 N2/N3, secuencia, despliegue y frontera de Unidad 3. |
| PL-03 · Modelo de datos | Aceptar y verificar | El DDL se ejecutó en MariaDB de XAMPP y se comprobaron 10 tablas. |
| PL-04 · Wireframe | Aceptar | La maqueta R1/R2 fue comprobada mediante Apache con HTTP 200. |
| PL-05 · Repositorio | Aceptar con ajuste | Se añadió un criterio observable de reversión antes de la semana 7. |
| PL-06 · Auditoría | Aceptar parcialmente | Se documentaron inconsistencias que deben verificarse antes de semana 7. |

## Hipótesis arquitectónica vs decisión final

La hipótesis inicial no definía una separación formal de componentes; el ADR-001 estableció una arquitectura MVC en capas.

## Decisión que probablemente revisaremos en semana 7

Comprobar que la estructura diseñada funcione correctamente sobre XAMPP.
