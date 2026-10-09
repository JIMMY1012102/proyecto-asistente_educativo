# Documento de Diseño Técnico
## Asistente de Retroalimentación para Simulacros de Admisión (CNI)

---

## Overview

El **Asistente de Retroalimentación para Simulacros de Admisión del CNI** es una aplicación web desarrollada en PHP que automatiza la clasificación y análisis de resultados de simulacros de admisión del Colegio Nacional de Ica. El sistema procesa las respuestas de los estudiantes de 5.º de secundaria, calcula métricas de desempeño por tema y presenta retroalimentación personalizada según tres roles de usuario: Estudiante, Docente y Dirección.

Implementado como un monolito modular por dominio utilizando CodeIgniter 4, el sistema ofrece interfaces web intuitivas que permiten consultar errores por tema, comparar desempeño entre simulacros y generar reportes grupales e institucionales. Todos los datos son simulados conforme a la Ley N.º 29733 de Protección de Datos Personales, asegurando la privacidad de los menores de edad. El despliegue se realiza en servidores locales XAMPP con MySQL como motor de base de datos.

---

## Architecture

## Diagrama C4 Nivel 2 (Contenedores)

```mermaid
flowchart TB
    subgraph "Máquina del Laboratorio"
        subgraph "XAMPP Local"
            subgraph "Aplicación Web PHP"
                WebApp["Asistente CNI<br/>(CodeIgniter 4)"]
            end
            subgraph "Base de Datos"
                MySQL[(MySQL<br/>Datos Simulados)]
            end
        end
        subgraph "Cliente Web"
            Browser["Navegador<br/>(Chrome/Firefox)"]
        end
    end
    
    Browser -->|HTTP/HTTPS| WebApp
    WebApp -->|Consultas SQL| MySQL
```

---

## Diagrama C4 Nivel 3 (Componentes)

```mermaid
flowchart TB
    subgraph "Navegador Web"
        UI["Interfaz de Usuario<br/>(HTML + JavaScript)"]
    end
    
    subgraph "Aplicación PHP (CodeIgniter 4)"
        subgraph "Capa de Presentación"
            Router["Controlador de Rutas<br/>(Router CI4)"]
            AuthCtrl["Controlador de Autenticación"]
            EstudianteCtrl["Controlador Estudiante"]
            DocenteCtrl["Controlador Docente"]
            DireccionCtrl["Controlador Dirección"]
        end
        
        subgraph "Capa de Lógica de Negocio"
            AuthService["Servicio de Autenticación"]
            ReporteService["Servicio de Reportes"]
            CalculoService["Servicio de Cálculos"]
        end
        
        subgraph "Capa de Datos"
            AuthModel["Modelo Usuario"]
            SimulacroModel["Modelo Simulacro"]
            RespuestaModel["Modelo Respuesta"]
        end
    end
    
    subgraph "Base de Datos MySQL"
        Tables[("Tablas:<br/>usuarios, simulacros<br/>respuestas, temas")]
    end
    
    UI -->|HTTP Request| Router
    Router --> AuthCtrl
    Router --> EstudianteCtrl
    Router --> DocenteCtrl
    Router --> DireccionCtrl
    
    AuthCtrl --> AuthService
    EstudianteCtrl --> ReporteService
    DocenteCtrl --> ReporteService
    DireccionCtrl --> ReporteService
    
    ReporteService --> CalculoService
    AuthService --> AuthModel
    ReporteService --> SimulacroModel
    ReporteService --> RespuestaModel
    
    AuthModel --> Tables
    SimulacroModel --> Tables
    RespuestaModel --> Tables
```

---

## Diagrama de secuencia

### Caso de uso principal: "Estudiante consulta reporte individual"

```mermaid
sequenceDiagram
    participant Browser as Navegador
    participant Router as Router CI4
    participant Auth as Middleware Auth
    participant EstCtrl as Controlador Estudiante
    participant ReporteSvc as Servicio Reportes
    participant CalcSvc as Servicio Cálculos
    participant SimModel as Modelo Simulacro
    participant RespModel as Modelo Respuesta
    participant MySQL as Base de Datos MySQL
    participant View as Vista HTML

    Browser->>Router: GET /estudiante/reporte
    Router->>Auth: Verificar sesión
    Auth->>MySQL: SELECT usuario WHERE session_id=?
    MySQL-->>Auth: Datos del usuario
    Auth-->>Router: Usuario autenticado
    
    Router->>EstCtrl: mostrarReporte()
    EstCtrl->>ReporteSvc: generarReporteIndividual(id_estudiante)
    
    ReporteSvc->>SimModel: obtenerUltimoSimulacro(id_estudiante)
    SimModel->>MySQL: SELECT simulacro WHERE estudiante=? ORDER BY fecha DESC LIMIT 1
    MySQL-->>SimModel: Datos del simulacro
    SimModel-->>ReporteSvc: Simulacro más reciente
    
    ReporteSvc->>RespModel: obtenerRespuestas(id_estudiante, id_simulacro)
    RespModel->>MySQL: SELECT respuestas WHERE estudiante=? AND simulacro=?
    MySQL-->>RespModel: Lista de respuestas
    RespModel-->>ReporteSvc: Respuestas del estudiante
    
    ReporteSvc->>CalcSvc: calcularPorcentajePorTema(respuestas)
    CalcSvc-->>ReporteSvc: Resultados por tema
    
    ReporteSvc->>CalcSvc: ordenarTemasPorError(resultados)
    CalcSvc-->>ReporteSvc: Temas ordenados
    
    ReporteSvc-->>EstCtrl: Reporte generado
    EstCtrl->>View: cargar vista con datos
    View-->>Browser: HTML con reporte individual
```

---

## Diagrama de despliegue

```mermaid
flowchart TB
    subgraph "Máquina del Laboratorio CNI"
        subgraph "XAMPP (Windows/Linux)"
            subgraph "Apache Web Server"
                WebServer["Apache HTTP<br/>Puerto 80/443"]
                subgraph "Aplicación"
                    PHPApp["Asistente CNI<br/>(PHP 8.1+ / CodeIgniter 4)"]
                end
            end
            
            subgraph "MySQL Server"
                Database["MySQL 8.0<br/>Puerto 3306"]
                subgraph "Esquemas"
                    SimulacrosDB[("asistente_cni<br/>(datos simulados)")]
                end
            end
        end
        
        Browser1["Navegador Estudiante"]
        Browser2["Navegador Docente"] 
        Browser3["Navegador Dirección"]
    end
    
    Browser1 -.->|HTTP| WebServer
    Browser2 -.->|HTTP| WebServer
    Browser3 -.->|HTTP| WebServer
    
    WebServer --> PHPApp
    PHPApp --> Database
    Database --> SimulacrosDB
```

---

## Components and Interfaces

| Componente | Responsabilidad | Carpeta | Historias que satisface |
|---|---|---|---|
| **Controlador de Autenticación** | Gestionar login, logout y validación de credenciales | `app/Controllers/Auth.php` | Req. 1 - Autenticación por rol |
| **Middleware de Autenticación** | Verificar sesión activa en cada request | `app/Filters/AuthFilter.php` | Req. 1 - Control de acceso |
| **Controlador Estudiante** | Manejar requests del rol estudiante | `app/Controllers/Estudiante.php` | Req. 4, 5, 6 - Reportes y comparaciones de estudiante |
| **Controlador Docente** | Manejar requests del rol docente | `app/Controllers/Docente.php` | Req. 7, 8 - Reportes grupales y detalle individual |
| **Controlador Dirección** | Manejar requests del rol dirección | `app/Controllers/Direccion.php` | Req. 9 - Resumen institucional agregado |
| **Servicio de Reportes** | Orquestar generación de todos los reportes | `app/Services/ReporteService.php` | Req. 4, 7, 9 - Lógica común de reportes |
| **Servicio de Cálculos** | Calcular métricas y porcentajes | `app/Services/CalculoService.php` | Req. 3, 5 - Procesamiento y clasificación |
| **Modelo Usuario** | Gestionar datos de usuarios y roles | `app/Models/UsuarioModel.php` | Req. 1 - Autenticación y roles |
| **Modelo Simulacro** | Gestionar datos de simulacros | `app/Models/SimulacroModel.php` | Req. 2, 4 - Procesamiento de simulacros |
| **Modelo Respuesta** | Gestionar respuestas de estudiantes | `app/Models/RespuestaModel.php` | Req. 2, 3 - Clasificación de errores |
| **Vistas HTML** | Presentar interfaces por rol | `app/Views/` | Todas - Interfaz de usuario |
| **JavaScript Frontend** | Interacciones dinámicas y AJAX | `public/assets/js/` | Todas - Experiencia de usuario |

---

## Data Models

El sistema utiliza una base de datos MySQL con datos simulados que incluye las siguientes entidades principales:

- **Usuarios**: Almacena estudiantes, docentes y dirección con sus roles y credenciales
- **Simulacros**: Registra las sesiones de evaluación con fechas y metadatos  
- **Respuestas**: Guarda las respuestas individuales de cada estudiante por simulacro
- **Temas**: Cataloga las áreas temáticas para clasificación de errores

La estructura relacional permite vincular respuestas con estudiantes y simulacros para generar los reportes por tema requeridos por cada rol de usuario.

---

## Punto de extensión para la Unidad 3

En la **Unidad 3**, se integrará un **módulo de conversación** que permitirá a los usuarios formular consultas en lenguaje natural español. Este módulo se conectará como un **controlador adicional** (`app/Controllers/Chat.php`) dentro de la arquitectura existente sin afectar la funcionalidad core.

**Punto de integración previsto:**
- **Ruta**: `/chat` - Endpoint POST para recibir consultas en texto libre
- **Flujo**: El controlador de chat interpretará la intención del usuario y redirigirá internamente a los servicios de reportes existentes
- **Datos**: Utilizará los mismos modelos y servicios ya implementados, manteniendo la consistencia arquitectónica
- **Interfaz**: Se agregará un widget de chat en las vistas existentes sin modificar la navegación principal

Este diseño permite una integración no invasiva del módulo conversacional, manteniendo la separación de responsabilidades y reutilizando toda la lógica de negocio ya desarrollada.

---

## Decisiones no tomadas

Las siguientes decisiones quedan pendientes para el diseño detallado e implementación:

1. **Esquema detallado de base de datos**: Definición exacta de índices, claves foráneas y constraints específicos de MySQL
2. **Estrategia de sesiones**: Implementación específica de manejo de sesiones (archivos, base de datos, o memoria)  
3. **Validaciones de formularios**: Reglas de validación detalladas para cada campo de entrada de datos
4. **Manejo de archivos temporales**: Estrategia para caches de reportes y archivos de trabajo temporal
5. **Logging y auditoría**: Implementación específica del sistema de trazabilidad de accesos requerido por Ley 29733
6. **Configuración de entorno**: Variables de configuración específicas para desarrollo, pruebas y producción
7. **Estrategia de backup**: Procedimientos de respaldo de la base de datos simulada
8. **Optimizaciones de rendimiento**: Índices de base de datos y estrategias de caché para consultas frecuentes
9. **Diseño visual detallado**: Especificaciones de CSS, paleta de colores y elementos de interfaz específicos
10. **Pruebas automatizadas**: Framework y estrategia de testing para validación de funcionalidades