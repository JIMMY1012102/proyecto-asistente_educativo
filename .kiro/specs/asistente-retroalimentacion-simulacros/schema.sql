CREATE DATABASE IF NOT EXISTS asistente_cni
  CHARACTER SET utf8mb4
  COLLATE utf8mb4_unicode_ci;

USE asistente_cni;

CREATE TABLE IF NOT EXISTS usuario (
  usuario_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre_usuario VARCHAR(80) NOT NULL,
  contrasena_hash VARCHAR(255) NOT NULL,
  rol ENUM('estudiante', 'docente', 'direccion') NOT NULL,
  codigo_anonimo VARCHAR(40) NULL,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  fecha_creacion DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (usuario_id),
  UNIQUE KEY uq_usuario_nombre (nombre_usuario),
  UNIQUE KEY uq_usuario_codigo_anonimo (codigo_anonimo),
  KEY idx_usuario_rol_activo (rol, activo),
  CONSTRAINT chk_usuario_activo CHECK (activo IN (0, 1)),
  CONSTRAINT chk_usuario_codigo_anonimo CHECK (
    (rol = 'estudiante' AND codigo_anonimo IS NOT NULL)
    OR (rol <> 'estudiante' AND codigo_anonimo IS NULL)
  )
) ENGINE=InnoDB
  COMMENT='Componente propietario: Modelo Usuario; cuentas, roles y código anonimizado (Req. 1, 11)';

CREATE TABLE IF NOT EXISTS grupo (
  grupo_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  codigo_grupo VARCHAR(30) NOT NULL,
  nivel VARCHAR(30) NOT NULL,
  seccion VARCHAR(20) NOT NULL,
  activo TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (grupo_id),
  UNIQUE KEY uq_grupo_codigo (codigo_grupo),
  UNIQUE KEY uq_grupo_nivel_seccion (nivel, seccion),
  KEY idx_grupo_nivel_activo (nivel, activo),
  CONSTRAINT chk_grupo_activo CHECK (activo IN (0, 1))
) ENGINE=InnoDB
  COMMENT='Componente propietario: Modelo Usuario (extensión para grupos); delimita grupos docentes e institucionales (Req. 7, 8, 9)';

CREATE TABLE IF NOT EXISTS docente_grupo (
  usuario_id BIGINT UNSIGNED NOT NULL,
  grupo_id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (usuario_id, grupo_id),
  KEY idx_docente_grupo_grupo (grupo_id),
  CONSTRAINT fk_docente_grupo_usuario
    FOREIGN KEY (usuario_id) REFERENCES usuario (usuario_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_docente_grupo_grupo
    FOREIGN KEY (grupo_id) REFERENCES grupo (grupo_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB
  COMMENT='Componente propietario: Modelo Usuario; asigna docentes a sus grupos (Req. 1.6, 7, 8)';

CREATE TABLE IF NOT EXISTS estudiante_grupo (
  usuario_id BIGINT UNSIGNED NOT NULL,
  grupo_id BIGINT UNSIGNED NOT NULL,
  fecha_asignacion DATE NOT NULL,
  vigente TINYINT(1) NOT NULL DEFAULT 1,
  PRIMARY KEY (usuario_id, grupo_id),
  KEY idx_estudiante_grupo_grupo_vigente (grupo_id, vigente),
  CONSTRAINT chk_estudiante_grupo_vigente CHECK (vigente IN (0, 1)),
  CONSTRAINT fk_estudiante_grupo_usuario
    FOREIGN KEY (usuario_id) REFERENCES usuario (usuario_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_estudiante_grupo_grupo
    FOREIGN KEY (grupo_id) REFERENCES grupo (grupo_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB
  COMMENT='Componente propietario: Modelo Usuario; registra la pertenencia de estudiantes a grupos (Req. 7, 8, 9)';

CREATE TABLE IF NOT EXISTS simulacro (
  simulacro_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(120) NOT NULL,
  fecha_aplicacion DATE NOT NULL,
  fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  descripcion VARCHAR(255) NULL,
  PRIMARY KEY (simulacro_id),
  KEY idx_simulacro_fecha (fecha_aplicacion),
  KEY idx_simulacro_registro (fecha_registro),
  KEY idx_simulacro_nombre (nombre)
) ENGINE=InnoDB
  COMMENT='Componente propietario: Modelo Simulacro; identifica evaluaciones y fechas (Req. 2, 4, 5, 7, 9)';

CREATE TABLE IF NOT EXISTS simulacro_grupo (
  simulacro_id BIGINT UNSIGNED NOT NULL,
  grupo_id BIGINT UNSIGNED NOT NULL,
  PRIMARY KEY (simulacro_id, grupo_id),
  KEY idx_simulacro_grupo_grupo (grupo_id),
  CONSTRAINT fk_simulacro_grupo_simulacro
    FOREIGN KEY (simulacro_id) REFERENCES simulacro (simulacro_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_simulacro_grupo_grupo
    FOREIGN KEY (grupo_id) REFERENCES grupo (grupo_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB
  COMMENT='Componente propietario: Modelo Simulacro (extensión); registra qué grupos rindieron cada evaluación (Req. 7.5, 9.6, 9.7)';

CREATE TABLE IF NOT EXISTS tema (
  tema_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  nombre VARCHAR(100) NOT NULL,
  descripcion VARCHAR(255) NULL,
  PRIMARY KEY (tema_id),
  UNIQUE KEY uq_tema_nombre (nombre)
) ENGINE=InnoDB
  COMMENT='Componente propietario: Servicio de Cálculos; clasifica preguntas y resultados por tema (Req. 3, 6, 7, 9)';

CREATE TABLE IF NOT EXISTS pregunta (
  pregunta_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  simulacro_id BIGINT UNSIGNED NOT NULL,
  tema_id BIGINT UNSIGNED NOT NULL,
  numero_pregunta SMALLINT UNSIGNED NOT NULL,
  opcion_correcta CHAR(1) NOT NULL,
  PRIMARY KEY (pregunta_id),
  UNIQUE KEY uq_pregunta_simulacro_numero (simulacro_id, numero_pregunta),
  KEY idx_pregunta_tema_simulacro (tema_id, simulacro_id),
  CONSTRAINT chk_pregunta_numero CHECK (numero_pregunta > 0),
  CONSTRAINT chk_pregunta_opcion_correcta CHECK (opcion_correcta IN ('A', 'B', 'C', 'D', 'E')),
  CONSTRAINT fk_pregunta_simulacro
    FOREIGN KEY (simulacro_id) REFERENCES simulacro (simulacro_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_pregunta_tema
    FOREIGN KEY (tema_id) REFERENCES tema (tema_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB
  COMMENT='Componente propietario: Modelo Simulacro y Servicio de Cálculos; permite contar preguntas por tema y definir respuestas correctas (Req. 2.5, 3.1, 3.3, 3.5)';

CREATE TABLE IF NOT EXISTS respuesta (
  usuario_id BIGINT UNSIGNED NOT NULL,
  pregunta_id BIGINT UNSIGNED NOT NULL,
  opcion_seleccionada CHAR(1) NOT NULL,
  fecha_registro DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (usuario_id, pregunta_id),
  KEY idx_respuesta_pregunta (pregunta_id),
  CONSTRAINT chk_respuesta_opcion CHECK (opcion_seleccionada IN ('A', 'B', 'C', 'D', 'E')),
  CONSTRAINT fk_respuesta_usuario
    FOREIGN KEY (usuario_id) REFERENCES usuario (usuario_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT,
  CONSTRAINT fk_respuesta_pregunta
    FOREIGN KEY (pregunta_id) REFERENCES pregunta (pregunta_id)
    ON UPDATE RESTRICT ON DELETE RESTRICT
) ENGINE=InnoDB
  COMMENT='Componente propietario: Modelo Respuesta; conserva respuestas originales para cálculos y reportes (Req. 2, 3, 4, 5, 7, 8, 9)';

CREATE TABLE IF NOT EXISTS registro_acceso (
  registro_acceso_id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
  usuario_id BIGINT UNSIGNED NULL,
  rol_activo ENUM('estudiante', 'docente', 'direccion') NULL,
  tipo_evento ENUM('consulta_datos', 'intento_escritura', 'acceso_denegado', 'inicio_sesion') NOT NULL,
  tipo_consulta VARCHAR(80) NOT NULL,
  codigo_resultado SMALLINT UNSIGNED NULL,
  fecha_hora DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (registro_acceso_id),
  KEY idx_registro_acceso_usuario_fecha (usuario_id, fecha_hora),
  KEY idx_registro_acceso_evento_fecha (tipo_evento, fecha_hora),
  CONSTRAINT fk_registro_acceso_usuario
    FOREIGN KEY (usuario_id) REFERENCES usuario (usuario_id)
    ON UPDATE RESTRICT ON DELETE SET NULL
) ENGINE=InnoDB
  COMMENT='Componente propietario: Middleware de Autenticación (extensión de auditoría); registra accesos sin almacenar resultados personales (Req. 2.3, 8.5, 11.3, 11.4)';