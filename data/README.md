# Base de Datos SQLite - Asistente de Retroalimentación CNI

Este directorio contiene el esquema y herramientas para la base de datos SQLite del Asistente de Retroalimentación para Simulacros de Admisión del CNI.

## ⚖️ Cumplimiento Legal

**IMPORTANTE**: Este sistema cumple estrictamente con la **Ley N.º 29733 de Protección de Datos Personales**. Todos los datos utilizados son **simulados y ficticios**. No se almacenan, procesan ni transmiten datos reales de estudiantes menores de edad.

## 📁 Archivos

| Archivo | Descripción | Propósito |
|---------|-------------|-----------|
| `schema.sql` | Esquema completo de la base de datos SQLite | Define todas las tablas, relaciones, índices y vistas |
| `create_database.py` | Script para crear la base de datos | Ejecuta el esquema y verifica la estructura |
| `asistente_cni.db` | Base de datos SQLite (generado) | Base de datos principal del sistema |
| `seed_simulados.py` | Generador de datos simulados (futuro) | Poblará la BD con datos ficticios para pruebas |

## 🏗️ Estructura de la Base de Datos

### Tablas Principales

1. **`usuario`** - Cuentas de usuarios con roles (estudiante, docente, dirección)
2. **`grupo`** - Grupos de estudiantes por nivel y sección
3. **`simulacro`** - Evaluaciones de admisión aplicadas
4. **`tema`** - Áreas del conocimiento evaluadas
5. **`pregunta`** - Preguntas de cada simulacro por tema
6. **`respuesta`** - Respuestas de estudiantes a preguntas específicas

### Tablas de Relación

- **`docente_grupo`** - Asignación de docentes a grupos
- **`estudiante_grupo`** - Pertenencia de estudiantes a grupos
- **`simulacro_grupo`** - Qué grupos rindieron cada simulacro

### Tabla de Auditoría

- **`registro_acceso`** - Log de accesos al sistema sin datos personales

### Vistas Optimizadas

- **`estudiantes_activos`** - Estudiantes con sus grupos activos
- **`docentes_grupos`** - Docentes con sus grupos asignados
- **`simulacros_con_estadisticas`** - Simulacros con conteos básicos

## 🚀 Uso

### Crear la Base de Datos

```bash
# Desde el directorio del proyecto
cd data
python create_database.py
```

### Desde Python

```python
from data.create_database import create_database, verify_database_structure

# Crear la base de datos
success = create_database()

# Verificar la estructura
if success:
    verify_database_structure()
```

### Conexión desde la Aplicación

```python
import sqlite3
from pathlib import Path

# Ruta a la base de datos
DB_PATH = Path(__file__).parent / "data" / "asistente_cni.db"

# Conectar con foreign keys habilitadas
conn = sqlite3.connect(DB_PATH)
conn.execute("PRAGMA foreign_keys = ON")
```

## 📊 Requisitos Implementados

- **Req. 11.1**: Base de datos con datos simulados únicamente
- **Req. 1.1-1.7**: Estructura para autenticación y control de acceso por rol
- **Req. 2.1-2.5**: Tablas para procesamiento de simulacros
- **Req. 3.1-3.5**: Estructura para clasificación de errores por tema
- **Req. 4.1-4.6**: Soporte para reportes individuales de estudiantes
- **Req. 5.1-5.7**: Estructura para comparación entre simulacros
- **Req. 7.1-7.5**: Soporte para reportes grupales docentes
- **Req. 8.1-8.6**: Estructura para vista de detalle individual
- **Req. 9.1-9.7**: Soporte para resumen institucional agregado
- **Req. 11.3-11.4**: Tabla de auditoría para logging

## 🔒 Características de Seguridad

1. **Integridad Referencial**: Foreign keys habilitadas por defecto
2. **Validación de Datos**: CHECK constraints en campos críticos
3. **Anonimización**: Campo `codigo_anonimo` para estudiantes
4. **Auditoría**: Registro de accesos sin contenido personal
5. **Solo Lectura MCP**: Preparado para integración con servidor MCP de solo lectura

## 🔧 Configuración SQLite

El esquema incluye configuraciones optimizadas:

```sql
PRAGMA foreign_keys = ON;        -- Integridad referencial
PRAGMA journal_mode = WAL;       -- Mejor concurrencia
PRAGMA synchronous = NORMAL;     -- Balance rendimiento/durabilidad
PRAGMA temp_store = memory;      -- Tablas temp en memoria
PRAGMA mmap_size = 268435456;    -- 256MB memory-mapped I/O
```

## 📈 Índices de Rendimiento

Índices optimizados para las consultas más frecuentes:

- Autenticación por usuario y rol
- Búsqueda de estudiantes por grupo
- Consulta de simulacros por fecha
- Agregación de respuestas por tema
- Auditoría por usuario y fecha

## ⚠️ Notas Importantes

1. **Datos Simulados**: Todos los datos son ficticios y generados automáticamente
2. **No Datos Reales**: NUNCA usar datos personales reales de estudiantes
3. **Servidor MCP**: La aplicación accederá a esta BD solo a través del servidor MCP
4. **Solo Lectura**: El servidor MCP debe configurarse en modo solo lectura
5. **Backup**: Respaldar regularmente la BD con los datos simulados

## 🔄 Próximos Pasos

1. **Ejecutar**: `create_database.py` para crear la estructura
2. **Poblar**: Ejecutar `seed_simulados.py` (próxima tarea) para datos de prueba
3. **Configurar**: Servidor MCP de solo lectura apuntando a esta BD
4. **Integrar**: Conectar la aplicación FastAPI al servidor MCP

---

**Cumplimiento Legal**: Este sistema respeta la privacidad de menores de edad según la Ley N.º 29733 utilizando exclusivamente datos simulados durante todo el ciclo de desarrollo y operación.