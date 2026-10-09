# Descarte argumentado · Alternativa no elegida: PHP 8 con MVC propio

## Criterio decisivo

Reducir el riesgo de introducir errores de seguridad y mantenimiento al construir infraestructura básica desde cero.

## Driver que lo sustenta

**Seguridad**, trazada principalmente a R1 y R11 en `docs/arquitectura/drivers.md`.

## Por qué habría fallado en nuestro contexto

Con PHP 8 y MVC propio, el equipo tendría que diseñar y mantener manualmente elementos estructurales como enrutamiento, controladores, validación, organización de capas y mecanismos asociados a autenticación.

Dado que R1 y R11 colocan la seguridad entre los drivers prioritarios, dedicar la semana 7 a construir infraestructura propia aumentaría el riesgo de inconsistencias y errores antes de implementar las historias funcionales.

CodeIgniter 4 proporciona una estructura MVC definida y reduce esa carga inicial.

## Estado de la afirmación

**[VERIFICAR]** La instalación y ejecución de CodeIgniter 4 sobre XAMPP debe comprobarse antes de comenzar la implementación funcional de la semana 7.
