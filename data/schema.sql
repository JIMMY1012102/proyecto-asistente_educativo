-- Esquema de base de datos SQLite para el Asistente de Retroalimentación
-- Adaptado desde el esquema MySQL original para cumplir con los requisitos
-- Componente: Base de Datos SQLite con datos simulados
-- Requisitos: 11.1 - Datos simulados en cumplimiento de la Ley N.º 29733

-- Configuración inicial para SQLite
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
PRAGMA synchronous = NORMAL;
PRAGMA temp_store = memory;
PRAGMA mmap_size = 268435456; -- 256MB

-- Tabla: usuario
-- Componente propietario: Modelo Usuario
-- Almacena cuentas, roles y código anonimizado (Req. 1, 11)
CREATE TABLE IF NOT EXISTS usuario (
    usuario_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre_usuario TEXT NOT NULL UNIQUE,
    contrasena_hash TEXT NOT NULL,
    rol TEXT NOT NULL CHECK (rol IN ('estudiante', 'docente', 'direccion')),
    codigo_anonimo TEXT UNIQUE,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1)),
    fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    -- Constraint: estudiantes deben tener código anónimo, otros roles no
    CONSTRAINT chk_usuario_codigo_anonimo CHECK (
        (rol = 'estudiante' AND codigo_anonimo IS NOT NULL)
        OR (rol != 'estudiante' AND codigo_anonimo IS NULL)
    )
);

-- Índices para tabla usuario
CREATE INDEX IF NOT EXISTS idx_usuario_rol_activo ON usuario(rol, activo);
CREATE INDEX IF NOT EXISTS idx_usuario_codigo_anonimo ON usuario(codigo_anonimo);

-- Tabla: grupo
-- Componente propietario: Modelo Usuario (extensión para grupos)
-- Delimita grupos docentes e institucionales (Req. 7, 8, 9)
CREATE TABLE IF NOT EXISTS grupo (
    grupo_id INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_grupo TEXT NOT NULL UNIQUE,
    nivel TEXT NOT NULL,
    seccion TEXT NOT NULL,
    activo INTEGER NOT NULL DEFAULT 1 CHECK (activo IN (0, 1)),
    
    UNIQUE(nivel, seccion)
);

-- Índices para tabla grupo
CREATE INDEX IF NOT EXISTS idx_grupo_nivel_activo ON grupo(nivel, activo);

-- Tabla: docente_grupo
-- Componente propietario: Modelo Usuario
-- Asigna docentes a sus grupos (Req. 1.6, 7, 8)
CREATE TABLE IF NOT EXISTS docente_grupo (
    usuario_id INTEGER NOT NULL,
    grupo_id INTEGER NOT NULL,
    
    PRIMARY KEY (usuario_id, grupo_id),
    FOREIGN KEY (usuario_id) REFERENCES usuario(usuario_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    FOREIGN KEY (grupo_id) REFERENCES grupo(grupo_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- Índices para tabla docente_grupo
CREATE INDEX IF NOT EXISTS idx_docente_grupo_grupo ON docente_grupo(grupo_id);

-- Tabla: estudiante_grupo
-- Componente propietario: Modelo Usuario
-- Registra la pertenencia de estudiantes a grupos (Req. 7, 8, 9)
CREATE TABLE IF NOT EXISTS estudiante_grupo (
    usuario_id INTEGER NOT NULL,
    grupo_id INTEGER NOT NULL,
    fecha_asignacion DATE NOT NULL,
    vigente INTEGER NOT NULL DEFAULT 1 CHECK (vigente IN (0, 1)),
    
    PRIMARY KEY (usuario_id, grupo_id),
    FOREIGN KEY (usuario_id) REFERENCES usuario(usuario_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    FOREIGN KEY (grupo_id) REFERENCES grupo(grupo_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- Índices para tabla estudiante_grupo
CREATE INDEX IF NOT EXISTS idx_estudiante_grupo_grupo_vigente ON estudiante_grupo(grupo_id, vigente);

-- Tabla: simulacro
-- Componente propietario: Modelo Simulacro
-- Identifica evaluaciones y fechas (Req. 2, 4, 5, 7, 9)
CREATE TABLE IF NOT EXISTS simulacro (
    simulacro_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    fecha_aplicacion DATE NOT NULL,
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    descripcion TEXT
);

-- Índices para tabla simulacro
CREATE INDEX IF NOT EXISTS idx_simulacro_fecha ON simulacro(fecha_aplicacion);
CREATE INDEX IF NOT EXISTS idx_simulacro_registro ON simulacro(fecha_registro);
CREATE INDEX IF NOT EXISTS idx_simulacro_nombre ON simulacro(nombre);

-- Tabla: simulacro_grupo
-- Componente propietario: Modelo Simulacro (extensión)
-- Registra qué grupos rindieron cada evaluación (Req. 7.5, 9.6, 9.7)
CREATE TABLE IF NOT EXISTS simulacro_grupo (
    simulacro_id INTEGER NOT NULL,
    grupo_id INTEGER NOT NULL,
    
    PRIMARY KEY (simulacro_id, grupo_id),
    FOREIGN KEY (simulacro_id) REFERENCES simulacro(simulacro_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    FOREIGN KEY (grupo_id) REFERENCES grupo(grupo_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- Índices para tabla simulacro_grupo
CREATE INDEX IF NOT EXISTS idx_simulacro_grupo_grupo ON simulacro_grupo(grupo_id);

-- Tabla: tema
-- Componente propietario: Servicio de Cálculos
-- Clasifica preguntas y resultados por tema (Req. 3, 6, 7, 9)
CREATE TABLE IF NOT EXISTS tema (
    tema_id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE,
    descripcion TEXT
);

-- Tabla: pregunta
-- Componente propietario: Modelo Simulacro y Servicio de Cálculos
-- Permite contar preguntas por tema y definir respuestas correctas (Req. 2.5, 3.1, 3.3, 3.5)
CREATE TABLE IF NOT EXISTS pregunta (
    pregunta_id INTEGER PRIMARY KEY AUTOINCREMENT,
    simulacro_id INTEGER NOT NULL,
    tema_id INTEGER NOT NULL,
    numero_pregunta INTEGER NOT NULL CHECK (numero_pregunta > 0),
    opcion_correcta TEXT NOT NULL CHECK (opcion_correcta IN ('A', 'B', 'C', 'D', 'E')),
    
    UNIQUE(simulacro_id, numero_pregunta),
    FOREIGN KEY (simulacro_id) REFERENCES simulacro(simulacro_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    FOREIGN KEY (tema_id) REFERENCES tema(tema_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- Índices para tabla pregunta
CREATE INDEX IF NOT EXISTS idx_pregunta_tema_simulacro ON pregunta(tema_id, simulacro_id);

-- Tabla: respuesta
-- Componente propietario: Modelo Respuesta
-- Conserva respuestas originales para cálculos y reportes (Req. 2, 3, 4, 5, 7, 8, 9)
CREATE TABLE IF NOT EXISTS respuesta (
    usuario_id INTEGER NOT NULL,
    pregunta_id INTEGER NOT NULL,
    opcion_seleccionada TEXT NOT NULL CHECK (opcion_seleccionada IN ('A', 'B', 'C', 'D', 'E')),
    fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    PRIMARY KEY (usuario_id, pregunta_id),
    FOREIGN KEY (usuario_id) REFERENCES usuario(usuario_id) ON DELETE RESTRICT ON UPDATE RESTRICT,
    FOREIGN KEY (pregunta_id) REFERENCES pregunta(pregunta_id) ON DELETE RESTRICT ON UPDATE RESTRICT
);

-- Índices para tabla respuesta
CREATE INDEX IF NOT EXISTS idx_respuesta_pregunta ON respuesta(pregunta_id);
CREATE INDEX IF NOT EXISTS idx_respuesta_usuario_fecha ON respuesta(usuario_id, fecha_registro);

-- Tabla: registro_acceso
-- Componente propietario: Middleware de Autenticación (extensión de auditoría)
-- Registra accesos sin almacenar resultados personales (Req. 2.3, 8.5, 11.3, 11.4)
CREATE TABLE IF NOT EXISTS registro_acceso (
    registro_acceso_id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER,
    rol_activo TEXT CHECK (rol_activo IN ('estudiante', 'docente', 'direccion')),
    tipo_evento TEXT NOT NULL CHECK (tipo_evento IN ('consulta_datos', 'intento_escritura', 'acceso_denegado', 'inicio_sesion')),
    tipo_consulta TEXT NOT NULL,
    codigo_resultado INTEGER,
    fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    
    FOREIGN KEY (usuario_id) REFERENCES usuario(usuario_id) ON DELETE SET NULL ON UPDATE RESTRICT
);

-- Índices para tabla registro_acceso
CREATE INDEX IF NOT EXISTS idx_registro_acceso_usuario_fecha ON registro_acceso(usuario_id, fecha_hora);
CREATE INDEX IF NOT EXISTS idx_registro_acceso_evento_fecha ON registro_acceso(tipo_evento, fecha_hora);

-- Vistas para consultas comunes y optimización

-- Vista: estudiantes_activos
-- Facilita consultas de estudiantes con sus grupos
CREATE VIEW IF NOT EXISTS estudiantes_activos AS
SELECT 
    u.usuario_id,
    u.codigo_anonimo,
    u.fecha_creacion,
    g.grupo_id,
    g.codigo_grupo,
    g.nivel,
    g.seccion,
    eg.fecha_asignacion
FROM usuario u
INNER JOIN estudiante_grupo eg ON u.usuario_id = eg.usuario_id
INNER JOIN grupo g ON eg.grupo_id = g.grupo_id
WHERE u.rol = 'estudiante' 
    AND u.activo = 1 
    AND g.activo = 1 
    AND eg.vigente = 1;

-- Vista: docentes_grupos
-- Facilita consultas de docentes con sus grupos asignados
CREATE VIEW IF NOT EXISTS docentes_grupos AS
SELECT 
    u.usuario_id,
    u.nombre_usuario,
    g.grupo_id,
    g.codigo_grupo,
    g.nivel,
    g.seccion
FROM usuario u
INNER JOIN docente_grupo dg ON u.usuario_id = dg.usuario_id
INNER JOIN grupo g ON dg.grupo_id = g.grupo_id
WHERE u.rol = 'docente' 
    AND u.activo = 1 
    AND g.activo = 1;

-- Vista: simulacros_con_estadisticas
-- Facilita consultas de simulacros con conteos básicos
CREATE VIEW IF NOT EXISTS simulacros_con_estadisticas AS
SELECT 
    s.simulacro_id,
    s.nombre,
    s.fecha_aplicacion,
    s.fecha_registro,
    s.descripcion,
    COUNT(DISTINCT sg.grupo_id) as total_grupos,
    COUNT(DISTINCT r.usuario_id) as total_estudiantes,
    COUNT(DISTINCT p.pregunta_id) as total_preguntas,
    COUNT(DISTINCT p.tema_id) as total_temas
FROM simulacro s
LEFT JOIN simulacro_grupo sg ON s.simulacro_id = sg.simulacro_id
LEFT JOIN pregunta p ON s.simulacro_id = p.simulacro_id
LEFT JOIN respuesta r ON p.pregunta_id = r.pregunta_id
GROUP BY s.simulacro_id, s.nombre, s.fecha_aplicacion, s.fecha_registro, s.descripcion;

-- Configuraciones adicionales de optimización
PRAGMA optimize;

-- Comentarios finales
-- Este esquema SQLite mantiene la funcionalidad del diseño original MySQL
-- pero adaptado para SQLite con las siguientes modificaciones principales:
-- 1. INTEGER PRIMARY KEY AUTOINCREMENT en lugar de BIGINT UNSIGNED AUTO_INCREMENT
-- 2. TEXT en lugar de VARCHAR/ENUM con CHECK constraints para validación
-- 3. INTEGER para booleanos con CHECK constraints
-- 4. Índices optimizados para las consultas más frecuentes
-- 5. Vistas para simplificar consultas comunes
-- 6. Configuración PRAGMA para optimización
-- 7. Mantiene todas las relaciones y constraints del diseño original