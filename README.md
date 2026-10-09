# Asistente de Retroalimentación para Simulacros de Admisión (CNI)

Sistema web FastAPI que automatiza el procesamiento y clasificación de resultados de simulacros de admisión del Colegio Nacional de Ica. Permite a estudiantes de 5.º de secundaria consultar sus errores por tema, a docentes revisar el rendimiento grupal, y a la dirección acceder a resúmenes institucionales agregados.

## Características Principales

- **Procesamiento automático** de respuestas de simulacros
- **Clasificación de errores** por tema y estudiante  
- **Reportes personalizados** según rol de usuario (Estudiante, Docente, Dirección)
- **Integración con Gemini API** para consultas en lenguaje natural
- **Cumplimiento Ley N.º 29733** con datos exclusivamente simulados
- **Servidor MCP de solo lectura** para acceso controlado a datos

## Tecnologías

- **Backend**: Python 3.11+, FastAPI
- **Frontend**: HTML + JavaScript simple
- **Base de datos**: SQLite con datos simulados
- **AI**: Gemini API para procesamiento de lenguaje natural
- **Autenticación**: JWT con control de acceso por rol

## Instalación y Configuración

### 1. Clonar el repositorio
```bash
git clone <url-del-repositorio>
cd Asistente_educativo_sistemas
```

### 2. Crear y activar entorno virtual
```bash
python -m venv venv

# Windows
.\venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno

Copiar el archivo de ejemplo y configurar las variables:

```bash
cp .env.example .env
```

Editar `.env` con los valores requeridos:
- `GEMINI_API_KEY`: Clave de API de Google Gemini (obligatorio)
- `JWT_SECRET_KEY`: Clave secreta para JWT (obligatorio)
- Otras variables según necesidades

### 5. Ejecutar la aplicación

```bash
python main.py
```

La aplicación estará disponible en `http://localhost:8000`

## Estructura del Proyecto

```
Asistente_educativo_sistemas/
├── app/
│   ├── models/          # Modelos de datos
│   ├── services/        # Lógica de negocio
│   ├── routers/         # Endpoints de la API
│   └── utils/           # Utilidades y configuración
├── static/
│   ├── css/             # Hojas de estilo
│   └── js/              # JavaScript frontend
├── templates/
│   ├── estudiante/      # Plantillas para estudiantes
│   ├── docente/         # Plantillas para docentes
│   ├── direccion/       # Plantillas para dirección
│   └── common/          # Plantillas compartidas
├── tests/
│   ├── unit/            # Pruebas unitarias
│   └── integration/     # Pruebas de integración
├── main.py              # Punto de entrada
├── requirements.txt     # Dependencias
└── .env.example         # Variables de entorno ejemplo
```

## Desarrollo

### Ejecutar tests
```bash
pytest tests/
```

### Ejecutar en modo desarrollo
```bash
# Con recarga automática
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Documentación API
Con la aplicación ejecutándose, visitar:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Roles de Usuario

### Estudiante
- Consultar reporte individual del último simulacro
- Comparar desempeño entre simulacros
- Recibir orientación de refuerzo por temas

### Docente  
- Ver reportes grupales por simulacro
- Consultar detalle individual de estudiantes de sus grupos
- Filtrar por simulacros específicos

### Dirección
- Acceder a resúmenes institucionales agregados
- Ver datos por nivel sin información individual de estudiantes
- Análisis estadístico por temas a nivel institucional

## Cumplimiento Legal

Este sistema cumple con la **Ley N.º 29733 de Protección de Datos Personales**:

- ✅ **Solo datos simulados**: No se procesan datos reales de estudiantes
- ✅ **Acceso controlado**: Servidor MCP de solo lectura
- ✅ **Anonimización**: Identificadores no vinculables a personas reales
- ✅ **Segregación por rol**: Acceso limitado según perfil de usuario

## Contribución

1. Fork del repositorio
2. Crear rama de característica (`git checkout -b feature/nueva-caracteristica`)
3. Commit de cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/nueva-caracteristica`)
5. Abrir Pull Request

## Licencia

Este proyecto es de uso interno del Colegio Nacional de Ica (CNI).
---

## Estado de arquitectura

**Arquitectura definida — semana 6**

### Equipo

- Malasquez Laredo Jimmy Alexander
- Alvarez Calagua Nia Elizabeth
- Rojas Castillo Sebastian Jaren

### Documentación

- `docs/adr/ADR-001.md` — Framework de aplicación
- `docs/adr/ADR-002.md` — Base de datos y persistencia
- `docs/adr/ADR-003.md` — Estructura del repositorio y ramas
- `docs/arquitectura/` — C4, secuencia, despliegue y modelo de datos
- `docs/maquetas/wireframe_v1.html` — Wireframe de semana 6

### Entorno previsto

- CodeIgniter 4
- PHP 8.x
- Apache de XAMPP
- MySQL/MariaDB de XAMPP

**Levantamiento final de CodeIgniter en XAMPP: [VERIFICAR EN SEMANA 7].**
