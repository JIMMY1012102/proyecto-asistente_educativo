# Documento de Arquitectura de Software

## Tarea 1: Comparativa y Selección del Estilo Arquitectónico

### 1. Supuestos

* **\[SUPUESTO\]** Se asigna la ponderación de las restricciones según su impacto técnico e institucional: Restricción Técnica (Stack y MCP), Normativa y Acceso se ponderan como Alta ($\times3$); Datos y Alcance como Media ($\times2$); Rol Docente como Baja ($\times1$).

* **\[SUPUESTO\]** La evaluación del stack se ajusta a las alternativas propuestas basadas en PHP para los tres estilos candidatos (a, b, c).

### 2. Matriz de Decisión

| **Driver / Restricción** | **Prioridad** | **(a) Monolito MVC en capas (PHP HTML)** | **(b) Monolito modular por dominio** | **(c) Cliente–Servidor: API REST (PHP) + SPA (JS)** | 
| **Eficiencia (H1,** $\le 5$**s)** | Alta ($\times3$) | **4**: Renderizado directo en servidor genera baja latencia ($<5$s). | **4**: Carga rápida por servidor con aislamiento modular sin overhead de red. | **3**: Latencia inicial alta por SPA y múltiples llamadas API HTTP. | 
| **Seguridad (confidencialidad, RF7)** | Alta ($\times3$) | **4**: Sesiones centralizadas en servidor minimizan exposición de endpoints públicos. | **5**: Aislamiento modular en servidor fortalece barreras de control de acceso. | **3**: Exposición de endpoints REST exige aseguramiento riguroso de cada ruta. | 
| **Seguridad (confidencialidad por rol, H6, RF6)** | Alta ($\times3$) | **4**: Validación centralizada en controladores simplifica el filtrado estricto por rol. | **5**: Módulos independientes imponen fronteras de autorización herméticas por cada rol. | **3**: Lógica de roles fragmentada entre interfaz cliente y validación backend. | 
| **Seguridad (integridad, MCP solo lectura)** | Alta ($\times3$) | **5**: Acceso directo controlado al MCP de lectura sin capas expuestas. | **5**: Encapsulamiento modular previene mutaciones de datos en la base subyacente. | **4**: Endpoints protegidos pero superficie expuesta a peticiones maliciosas externas. | 
| **Fiabilidad / Exactitud funcional (H3, H1)** | Alta ($\times3$) | **4**: Procesamiento síncrono en servidor evita inconsistencias en la capa visual. | **5**: Módulos aislados garantizan exactitud de cálculos sin efectos colaterales indeseados. | **3**: Manejo de estado en cliente puede provocar discrepancias de visualización. | 
| **Responsabilidad (trazabilidad, RNF4)** | Media ($\times2$) | **4**: Middleware centralizado permite registro directo y completo de cada solicitud. | **5**: Trazabilidad y logs segmentados por módulo facilitan la auditoría detallada. | **3**: Requiere correlacionar trazas entre el cliente JS y servicios REST. | 
| **Seguridad (secretos, RNF3)** | Media ($\times2$) | **5**: Claves API protegidas al 100% dentro de la capa servidor. | **5**: Variables de entorno y secretos totalmente resguardados en backend modular. | **3**: Alto riesgo de filtración si no se desacoplan correctamente credenciales. | 
| **Restricción Técnica: Stack** | Alta ($\times3$) | **5**: Implementación directa utilizando el lenguaje PHP solicitado sin dependencias adicionales. | **5**: Compatible totalmente con estructura monolítica modular basada en PHP. | **4**: Duplica tecnologías al requerir un entorno JS SPA y API. | 
| **Restricción Técnica: MCP solo lectura** | Alta ($\times3$) | **4**: Conexión limpia y directa con MCP de lectura sin intermediarios. | **5**: Módulo dedicado de lectura garantiza estricto control sobre la fuente. | **4**: Capa de servicios REST gestiona accesos de solo lectura correctamente. | 
| **Restricción Normativa: Ley 29733** | Alta ($\times3$) | **4**: Procesamiento de datos simulados restringido a la memoria del servidor. | **5**: Módulo de dominio aísla rigurosamente el tratamiento de datos sensibles. | **3**: Riesgo de almacenar o volcar datos simulados en el navegador. | 
| **Restricción Datos: Catálogo fijo** | Media ($\times2$) | **4**: Administración sencilla de catálogos mediante modelos centralizados tradicionales. | **5**: Dominio específico gestiona el catálogo de preguntas de forma autónoma. | **4**: Servicio REST expone catálogo en formato JSON consumido por cliente. | 
| **Restricción Org.: No reemplaza docente** | Baja ($\times1$) | **4**: Muestra avisos orientativos directamente generados desde la plantilla servidor. | **5**: Módulo pedagógico delimita el carácter exclusivamente orientativo de las respuestas. | **4**: Vistas en cliente JS renderizan disclaimers sin alterar la lógica. | 
| **Restricción Org.: Fuera de alcance** | Media ($\times2$) | **4**: Facilidad para deshabilitar rutas de modificación en el servidor web. | **5**: Estructura por módulos excluye completamente funcionalidades de escritura no requeridas. | **3**: Overhead para bloquear o restringir endpoints REST de escritura innecesarios. | 
| **Restricción Acceso: Autenticación por rol** | Alta ($\times3$) | **4**: Autenticación tradicional mediante sesiones y cookies seguras gestionadas centralmente. | **5**: Módulos independientes garantizan la aplicación rigurosa de políticas de acceso. | **3**: Exige implementar gestión compleja de tokens JWT en cliente/servidor. | 
| **TOTAL PONDERADO (Máx. 180 pts)** | — | **152 / 180** | **177 / 180** | **120 / 180** | 

### 3. Recomendación

Se recomienda el **Monolito modular por dominio, renderizado en servidor (b)**. Los dos drivers de mayor peso en la decisión fueron la **Seguridad (confidencialidad por rol)** y la **Restricción de integridad / MCP de solo lectura**, ya que el aislamiento en módulos independientes dentro del servidor ofrece un control hermético de accesos. Esta decisión debe revisarse si la plataforma requiere interacciones reactivas complejas en tiempo real o el desarrollo paralelo de una aplicación móvil.

### 4. Punto de Integración Futura

El agente conversacional (Unidad 3) se conectará como un **módulo de dominio independiente** dentro del monolito. Interactuará mediante servicios de aplicación internos con los módulos de expediente y documentos, procesando las consultas a Gemini desde el backend sin exponer credenciales ni lógica directa al cliente.

## Tarea 2: Registro de Decisión de Arquitectura (ADR-001)

### Título

**ADR-001: Selección del Framework de Aplicación**

### Estado

**Aceptado**

### Contexto

Se requiere seleccionar el framework base en PHP para la construcción del monolito modular por dominio. La elección está fuertemente condicionada por los siguientes drivers:

* **Mantenibilidad y estructura modular:** Capacidad de aislar dominios (ruta de titulación, documentos, expediente, etc.).

* **Velocidad de desarrollo e integración:** Eficiencia en la creación de vistas SSR y manejo de datos.

* **Entorno de ejecución local:** Requisito obligatorio de compatibilidad e instalación en servidor local XAMPP `[VERIFICAR]`.

* **Motor de base de datos:** El uso de MySQL ya se encuentra fijado previamente.

### Alternativas Evaluadas

#### 1. Laravel (versión estable vigente)

* **Ventajas:**

  * ORM (Eloquent) robusto ideal para modelar límites entre dominios.

  * Ecosistema maduro con soporte nativo para pruebas automatizadas y gestión de migraciones.

* **Desventajas:**

  * Mayor consumo de recursos de memoria en el servidor.

  * Requiere configuración específica de VirtualHost o reescritura de URL para su correcta ejecución en XAMPP `[VERIFICAR]`.

#### 2. CodeIgniter 4 (versión estable vigente)

* **Ventajas:**

  * Extremadamente ligero, con mínima huella de memoria y alto rendimiento.

  * Instalación y despliegue casi inmediato dentro de la carpeta `htdocs` de XAMPP `[VERIFICAR]`.

* **Desventajas:**

  * Menor disponibilidad de herramientas avanzadas para organizar arquitecturas modulares estrictas por dominio.

#### 3. PHP 8 con MVC Propio

* **Ventajas:**

  * Cero dependencias de terceros y control total sobre el código fuente.

* **Desventajas:**

  * Alto costo de desarrollo al requerir construir manualmente enrutamiento, ORM y mecanismos de seguridad.

  * Alta deuda técnica y riesgo de inconsistencias que deben validarse en XAMPP `[VERIFICAR]`.

### Decisión

En la evaluación técnica inicial, **Laravel (versión estable vigente)** y **CodeIgniter 4 (versión estable vigente)** empatan en términos de factibilidad técnica general. Se aplica como criterio de desempate la potencia de su ORM y las facilidades que ofrece para la separación estricta por módulos de dominio y testing automatizado, seleccionando **Laravel (versión estable vigente)**.

### Consecuencias y Deuda Aceptada

* **Consecuencias positivas:** Aceleración en el desarrollo gracias a su ecosistema, alta mantenibilidad y facilidades para estructurar módulos independientes.

* **Deuda aceptada:** Mayor huella de memoria en ejecución y la complejidad de preparar la configuración inicial del entorno local sobre XAMPP `[VERIFICAR]`.

### Criterio de Reversión

Si durante la fase de puesta en marcha (antes de la **semana 7**) la instalación o ejecución sobre XAMPP `[VERIFICAR]` presenta bloqueos insuperables de entorno o degradación severa de rendimiento, se revertirá la decisión hacia **CodeIgniter 4 (versión estable vigente)**.