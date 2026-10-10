-- =============================================
-- SCRIPT: SISTEMA DE GESTIÓN DE CURSOS Y ESTUDIANTES
-- Base de datos: Gestión de Cursos y Estudiantes
-- =============================================


-- =============================================
-- ELIMINAR TABLAS
-- =============================================

DROP TABLE IF EXISTS matricula;
DROP TABLE IF EXISTS curso;
DROP TABLE IF EXISTS docente;
DROP TABLE IF EXISTS alumno;
DROP TABLE IF EXISTS persona;
DROP TABLE IF EXISTS distrito;


-- =============================================
-- TABLA: distrito
-- =============================================

CREATE TABLE distrito (
    id_distrito SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL
);


-- =============================================
-- TABLA: persona
-- =============================================

CREATE TABLE persona (
    id_persona SERIAL PRIMARY KEY,
    dni TEXT UNIQUE NOT NULL,
    nombres TEXT NOT NULL,
    apellidos TEXT NOT NULL,
    telefono TEXT,
    correo TEXT UNIQUE,
    direccion TEXT
);


-- =============================================
-- TABLA: alumno
-- =============================================

CREATE TABLE alumno (
    id_alumno SERIAL PRIMARY KEY,
    codigo_alumno TEXT UNIQUE NOT NULL,
    id_persona INTEGER NOT NULL,
    id_distrito INTEGER NOT NULL,

    CONSTRAINT fk_alumno_persona
        FOREIGN KEY (id_persona)
        REFERENCES persona(id_persona),

    CONSTRAINT fk_alumno_distrito
        FOREIGN KEY (id_distrito)
        REFERENCES distrito(id_distrito)
);


-- =============================================
-- TABLA: docente
-- =============================================

CREATE TABLE docente (
    id_docente SERIAL PRIMARY KEY,
    especialidad TEXT NOT NULL,
    id_persona INTEGER NOT NULL,

    CONSTRAINT fk_docente_persona
        FOREIGN KEY (id_persona)
        REFERENCES persona(id_persona)
);


-- =============================================
-- TABLA: curso
-- =============================================

CREATE TABLE curso (
    id_curso SERIAL PRIMARY KEY,
    nombre TEXT NOT NULL,
    descripcion TEXT,
    creditos INTEGER NOT NULL,
    ciclo TEXT NOT NULL,
    horas_semanales INTEGER NOT NULL,
    id_docente INTEGER NOT NULL,

    CONSTRAINT fk_curso_docente
        FOREIGN KEY (id_docente)
        REFERENCES docente(id_docente),

    CONSTRAINT chk_creditos
        CHECK (creditos > 0),

    CONSTRAINT chk_horas
        CHECK (horas_semanales > 0)
);


-- =============================================
-- TABLA: matricula
-- =============================================

CREATE TABLE matricula (
    id_matricula SERIAL PRIMARY KEY,
    fecha_matricula DATE NOT NULL,
    estado TEXT NOT NULL,
    id_alumno INTEGER NOT NULL,
    id_curso INTEGER NOT NULL,

    CONSTRAINT fk_matricula_alumno
        FOREIGN KEY (id_alumno)
        REFERENCES alumno(id_alumno),

    CONSTRAINT fk_matricula_curso
        FOREIGN KEY (id_curso)
        REFERENCES curso(id_curso),

    CONSTRAINT chk_estado
        CHECK (estado IN ('ACTIVO', 'RETIRADO', 'FINALIZADO'))
);


-- =============================================
-- ÍNDICES
-- =============================================

CREATE INDEX ix_persona_dni
ON persona(dni);

CREATE INDEX ix_alumno_codigo
ON alumno(codigo_alumno);

CREATE INDEX ix_curso_nombre
ON curso(nombre);


-- =============================================
-- DATOS DE PRUEBA: DISTRITOS
-- =============================================

INSERT INTO distrito (nombre) VALUES
('Miraflores'),
('San Isidro'),
('Surco'),
('Callao'),
('San Miguel');


-- =============================================
-- DATOS DE PRUEBA: PERSONAS
-- =============================================

INSERT INTO persona
(dni, nombres, apellidos, telefono, correo, direccion)
VALUES
('71234567', 'Carlos', 'Ramirez Torres', '987654321',
'carlos.ramirez@gmail.com', 'Av. Larco 123'),

('72345678', 'Maria', 'Gonzales Flores', '986543210',
'maria.gonzales@gmail.com', 'Av. Arequipa 456'),

('73456789', 'Juan', 'Perez Castillo', '985432109',
'juan.perez@gmail.com', 'Jr. Lima 789'),

('74567890', 'Ana', 'Torres Mendoza', '984321098',
'ana.torres@gmail.com', 'Av. La Marina 321'),

('75678901', 'Luis', 'Fernandez Rojas', '983210987',
'luis.fernandez@gmail.com', 'Av. Javier Prado 654'),

('76789012', 'Sofia', 'Martinez Diaz', '982109876',
'sofia.martinez@gmail.com', 'Jr. Tacna 147'),

('77890123', 'Diego', 'Vargas Silva', '981098765',
'diego.vargas@gmail.com', 'Av. Brasil 258'),

('78901234', 'Valeria', 'Castro Luna', '980987654',
'valeria.castro@gmail.com', 'Av. Universitaria 369');


-- =============================================
-- DATOS DE PRUEBA: ALUMNOS
-- =============================================

INSERT INTO alumno
(codigo_alumno, id_persona, id_distrito)
VALUES
('ALU2026001', 1, 1),
('ALU2026002', 2, 2),
('ALU2026003', 3, 3),
('ALU2026004', 4, 4),
('ALU2026005', 5, 5);


-- =============================================
-- DATOS DE PRUEBA: DOCENTES
-- =============================================

INSERT INTO docente
(especialidad, id_persona)
VALUES
('Programación', 6),
('Base de Datos', 7),
('Redes y Comunicaciones', 8);


-- =============================================
-- DATOS DE PRUEBA: CURSOS
-- =============================================

INSERT INTO curso
(nombre, descripcion, creditos, ciclo, horas_semanales, id_docente)
VALUES
(
    'Programación I',
    'Fundamentos de programación y lógica.',
    4,
    'I',
    6,
    1
),

(
    'Base de Datos',
    'Diseño y administración de bases de datos.',
    4,
    'III',
    6,
    2
),

(
    'Redes de Computadoras',
    'Fundamentos de redes y comunicaciones.',
    3,
    'IV',
    5,
    3
),

(
    'Programación Web',
    'Desarrollo de aplicaciones web.',
    4,
    'V',
    6,
    1
);


-- =============================================
-- DATOS DE PRUEBA: MATRÍCULAS
-- =============================================

INSERT INTO matricula
(fecha_matricula, estado, id_alumno, id_curso)
VALUES
('2026-03-10', 'ACTIVO', 1, 1),
('2026-03-10', 'ACTIVO', 1, 2),
('2026-03-11', 'ACTIVO', 2, 1),
('2026-03-11', 'FINALIZADO', 3, 1),
('2026-03-12', 'ACTIVO', 3, 3),
('2026-03-13', 'RETIRADO', 4, 2),
('2026-03-14', 'ACTIVO', 4, 4),
('2026-03-15', 'ACTIVO', 5, 2);


-- =============================================
-- MOSTRAR REGISTROS
-- =============================================

SELECT * FROM distrito;

SELECT * FROM persona;

SELECT * FROM alumno;

SELECT * FROM docente;

SELECT * FROM curso;

SELECT * FROM matricula;


-- =============================================
-- VERIFICAR REGISTROS
-- =============================================

SELECT 'distrito' AS tabla, COUNT(*) AS registros
FROM distrito

UNION ALL

SELECT 'persona', COUNT(*)
FROM persona

UNION ALL

SELECT 'alumno', COUNT(*)
FROM alumno

UNION ALL

SELECT 'docente', COUNT(*)
FROM docente

UNION ALL

SELECT 'curso', COUNT(*)
FROM curso

UNION ALL

SELECT 'matricula', COUNT(*)
FROM matricula;
