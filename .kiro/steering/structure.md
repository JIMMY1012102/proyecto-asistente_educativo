# Estructura del proyecto

La estructura sigue la decisión de ADR-001: CodeIgniter 4 con arquitectura MVC en capas.

| Componente | Ubicación prevista |
|---|---|
| Enrutador | app/Config/Routes.php |
| Controlador de Autenticación | app/Controllers/AutenticacionController.php |
| Filtro de Autenticación | app/Filters/AutenticacionFilter.php |
| Filtro de Rol | app/Filters/RolFilter.php |
| Controlador Estudiante | app/Controllers/EstudianteController.php |
| Controlador Docente | app/Controllers/DocenteController.php |
| Controlador Dirección | app/Controllers/DireccionController.php |
| Servicio de Autenticación | app/Services/AutenticacionService.php |
| Servicio de Reportes | app/Services/ReporteService.php |
| Servicio de Cálculos | app/Services/CalculoService.php |
| Servicio de Auditoría | app/Services/AuditoriaService.php |
| Modelo Usuario | app/Models/UsuarioModel.php |
| Modelo Simulacro | app/Models/SimulacroModel.php |
| Modelo Respuesta | app/Models/RespuestaModel.php |
| Modelo Registro Acceso | app/Models/RegistroAccesoModel.php |
| Vistas por rol | app/Views/ |

## Reglas

- Todo componente debe trazar a requirements.md.
- Secretos únicamente en .env.
- No implementar agente conversacional, modelos de IA ni MCP hasta la Unidad 3.
- Toda tabla nueva exige actualizar docs/arquitectura/modelo_datos.md.
