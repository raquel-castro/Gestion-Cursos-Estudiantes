import os
import psycopg2
from psycopg2.extras import RealDictCursor

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")
DB_NAME = os.getenv("DB_NAME", "db_gestion_cursos_estudiantes")
DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")


def obtener_conexion():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )


def Inicializar():
    conn = obtener_conexion()
    try:
        with conn.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS distrito (
                    id_distrito INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    nombre TEXT NOT NULL
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS persona (
                    id_persona INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    dni TEXT NOT NULL UNIQUE,
                    nombres TEXT NOT NULL,
                    apellidos TEXT NOT NULL,
                    telefono TEXT,
                    correo TEXT UNIQUE,
                    direccion TEXT
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alumno (
                    id_alumno INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    codigo_alumno TEXT NOT NULL UNIQUE,
                    id_persona INTEGER NOT NULL,
                    id_distrito INTEGER NOT NULL,
                    CONSTRAINT fk_alumno_persona FOREIGN KEY (id_persona) REFERENCES persona(id_persona),
                    CONSTRAINT fk_alumno_distrito FOREIGN KEY (id_distrito) REFERENCES distrito(id_distrito)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS docente (
                    id_docente INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    especialidad TEXT NOT NULL,
                    id_persona INTEGER NOT NULL,
                    CONSTRAINT fk_docente_persona FOREIGN KEY (id_persona) REFERENCES persona(id_persona)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS curso (
                    id_curso INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    nombre TEXT NOT NULL,
                    descripcion TEXT,
                    creditos INTEGER NOT NULL CHECK (creditos > 0),
                    ciclo TEXT NOT NULL,
                    horas_semanales INTEGER NOT NULL CHECK (horas_semanales > 0),
                    id_docente INTEGER NOT NULL,
                    CONSTRAINT fk_curso_docente FOREIGN KEY (id_docente) REFERENCES docente(id_docente)
                )
            """)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS matricula (
                    id_matricula INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
                    fecha_matricula DATE NOT NULL,
                    estado TEXT NOT NULL CHECK (estado IN ('ACTIVO', 'RETIRADO', 'FINALIZADO')),
                    id_alumno INTEGER NOT NULL,
                    id_curso INTEGER NOT NULL,
                    CONSTRAINT fk_matricula_alumno FOREIGN KEY (id_alumno) REFERENCES alumno(id_alumno),
                    CONSTRAINT fk_matricula_curso FOREIGN KEY (id_curso) REFERENCES curso(id_curso),
                    CONSTRAINT uq_matricula_alumno_curso UNIQUE (id_alumno, id_curso)
                )
            """)
            cursor.execute("""
                DO $$
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM information_schema.columns
                        WHERE table_name = 'matricula'
                        AND column_name = 'fecha_matricula'
                        AND data_type <> 'date'
                    ) THEN
                        ALTER TABLE matricula
                        ALTER COLUMN fecha_matricula TYPE DATE
                        USING fecha_matricula::date;
                    END IF;
                END $$;
            """)
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_persona_correo_lower ON persona (LOWER(correo)) WHERE correo IS NOT NULL")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_distrito_nombre ON distrito (LOWER(nombre))")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_curso_nombre ON curso (LOWER(nombre))")
            cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ux_matricula_alumno_curso ON matricula(id_alumno, id_curso)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_persona_dni ON persona(dni)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_alumno_codigo ON alumno(codigo_alumno)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_alumno_distrito ON alumno(id_distrito)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_docente_persona ON docente(id_persona)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_curso_nombre ON curso(nombre)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_curso_docente ON curso(id_docente)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_matricula_alumno ON matricula(id_alumno)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_matricula_curso ON matricula(id_curso)")
            cursor.execute("CREATE INDEX IF NOT EXISTS ix_matricula_estado ON matricula(estado)")
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


if __name__ == "__main__":
    Inicializar()
    print("Base de datos PostgreSQL creada correctamente.")
