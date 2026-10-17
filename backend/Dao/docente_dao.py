
import psycopg2
from config.logger import Logger
from config.base_datos import obtener_conexion
from models.docente import Docente


# ==========================================
# EXCEPCIONES
# ==========================================

class DocenteNoEncontradoError(Exception):
    def __init__(self, docente_id):
        super().__init__(
            f"Docente ID={docente_id} no encontrado"
        )


class DocenteConCursosError(Exception):
    def __init__(self, docente_id):
        super().__init__(
            f"Docente ID={docente_id} no se puede eliminar: "
            f"tiene cursos asociados"
        )


# ==========================================
# CLASE DOCENTE DAO
# ==========================================

class DocenteDAO:

    def __init__(self):
        self.__log = Logger()

    # ==========================================
    # INSERTAR
    # ==========================================

    def insertar(self, docente):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO docente (
                    especialidad,
                    id_persona
                )
                VALUES (%s, %s)
                RETURNING id_docente
                """,
                (
                    docente.especialidad,
                    docente.id_persona
                )
            )

            fila = cursor.fetchone()
            docente.id_docente = fila["id_docente"]

            conn.commit()

        except psycopg2.IntegrityError:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

        self.__log.info(
            f"Docente agregado: "
            f"Especialidad {docente.especialidad} "
            f"(ID={docente.id_docente})"
        )

        return docente

    # ==========================================
    # BUSCAR POR ID
    # ==========================================

    def buscar_por_id(self, docente_id):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT *
                FROM docente
                WHERE id_docente = %s
                """,
                (docente_id,)
            )

            fila = cursor.fetchone()

            return (
                self.__fila_a_docente(fila)
                if fila else None
            )

        finally:
            cursor.close()
            conn.close()

    # ==========================================
    # OBTENER TODOS
    # ==========================================

    def obtener_todos(self):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT *
                FROM docente
                ORDER BY especialidad
                """
            )

            return [
                self.__fila_a_docente(fila)
                for fila in cursor.fetchall()
            ]

        finally:
            cursor.close()
            conn.close()

    # ==========================================
    # BUSCAR
    # ==========================================

    def buscar(self, especialidad=None, nombre=None):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            condiciones = []
            valores = []

            if especialidad:
                condiciones.append(
                    "d.especialidad ILIKE %s"
                )
                valores.append(
                    f"%{especialidad.strip()}%"
                )

            if nombre:
                condiciones.append(
                    "(p.nombres ILIKE %s OR "
                    "p.apellidos ILIKE %s)"
                )
                patron = f"%{nombre.strip()}%"
                valores.extend([patron, patron])

            if not condiciones:
                return []

            cursor.execute(
                f"""
                SELECT d.*
                FROM docente d
                JOIN persona p
                    ON p.id_persona = d.id_persona
                WHERE {' AND '.join(condiciones)}
                ORDER BY d.especialidad
                """,
                tuple(valores)
            )

            return [
                self.__fila_a_docente(fila)
                for fila in cursor.fetchall()
            ]

        finally:
            cursor.close()
            conn.close()

    # ==========================================
    # ACTUALIZAR
    # ==========================================

    def actualizar(
        self,
        docente_id,
        especialidad=None,
        id_persona=None
    ):
        d = self.buscar_por_id(docente_id)

        if not d:
            self.__log.error(
                f"Actualizar fallido: "
                f"Docente ID={docente_id} no existe"
            )
            raise DocenteNoEncontradoError(docente_id)

        nueva_especialidad = (
            especialidad
            if especialidad is not None
            else d.especialidad
        )

        nueva_persona = (
            id_persona
            if id_persona is not None
            else d.id_persona
        )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE docente
                SET especialidad = %s,
                    id_persona = %s
                WHERE id_docente = %s
                """,
                (
                    nueva_especialidad,
                    nueva_persona,
                    docente_id
                )
            )

            conn.commit()

        except psycopg2.IntegrityError:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

        d.especialidad = nueva_especialidad
        d.id_persona = nueva_persona

        self.__log.info(
            f"Docente actualizado: ID={docente_id}"
        )

        return d

    # ==========================================
    # ELIMINAR
    # ==========================================

    def eliminar(self, docente_id):
        d = self.buscar_por_id(docente_id)

        if not d:
            raise DocenteNoEncontradoError(docente_id)

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                DELETE FROM docente
                WHERE id_docente = %s
                """,
                (docente_id,)
            )

            conn.commit()

        except psycopg2.IntegrityError:
            conn.rollback()
            raise DocenteConCursosError(docente_id)

        finally:
            cursor.close()
            conn.close()

        self.__log.info(
            f"Docente eliminado: ID={docente_id}"
        )

    # ==========================================
    # TOTAL
    # ==========================================

    def total(self):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT COUNT(*) AS total
                FROM docente
                """
            )

            return cursor.fetchone()["total"]

        finally:
            cursor.close()
            conn.close()

    # ==========================================
    # ASIGNAR CURSOS AL DOCENTE
    # ==========================================

    def asignar_cursos(self, docente_id, ids_cursos):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT especialidad
                FROM docente
                WHERE id_docente = %s
                FOR UPDATE
                """,
                (docente_id,)
            )

            docente = cursor.fetchone()

            if not docente:
                raise DocenteNoEncontradoError(docente_id)

            ids_cursos = list(dict.fromkeys(ids_cursos))

            if ids_cursos:
                cursor.execute(
                    """
                    SELECT id_curso
                    FROM curso
                    WHERE id_curso = ANY(%s)
                      AND UPPER(TRIM(carrera)) =
                          UPPER(TRIM(%s))
                    """,
                    (
                        ids_cursos,
                        docente["especialidad"]
                    )
                )

                encontrados = {
                    fila["id_curso"]
                    for fila in cursor.fetchall()
                }

                if encontrados != set(ids_cursos):
                    raise ValueError(
                        "Los cursos seleccionados no existen "
                        "o no pertenecen a la carrera del docente."
                    )

            cursor.execute(
                """
                DELETE FROM docente_curso
                WHERE id_docente = %s
                """,
                (docente_id,)
            )

            for id_curso in ids_cursos:
                cursor.execute(
                    """
                    INSERT INTO docente_curso (
                        id_docente,
                        id_curso
                    )
                    VALUES (%s, %s)
                    """,
                    (docente_id, id_curso)
                )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    # ==========================================
    # CONSULTAR CURSOS DEL DOCENTE
    # ==========================================

    def obtener_cursos_docente(self, docente_id):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT
                    c.id_curso,
                    c.nombre,
                    c.carrera,
                    c.ciclo,
                    c.creditos,
                    c.horas_semanales
                FROM docente_curso dc
                JOIN curso c
                    ON c.id_curso = dc.id_curso
                WHERE dc.id_docente = %s
                ORDER BY
                    CASE c.ciclo
                        WHEN 'I' THEN 1
                        WHEN 'II' THEN 2
                        WHEN 'III' THEN 3
                        WHEN 'IV' THEN 4
                        WHEN 'V' THEN 5
                        WHEN 'VI' THEN 6
                        ELSE 99
                    END,
                    c.nombre
                """,
                (docente_id,)
            )

            return [
                dict(fila)
                for fila in cursor.fetchall()
            ]

        finally:
            cursor.close()
            conn.close()

    # ==========================================
    # REGISTRAR DOCENTE CON SUS CURSOS
    # ==========================================

    def insertar_con_cursos(self, docente, ids_cursos):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            ids_cursos = list(dict.fromkeys(ids_cursos))

            # Verificar que la persona exista
            cursor.execute(
                """
                SELECT id_persona
                FROM persona
                WHERE id_persona = %s
                """,
                (docente.id_persona,)
            )

            if not cursor.fetchone():
                raise ValueError(
                    "La persona seleccionada no existe."
                )

            # Verificar que los cursos correspondan
            # a la carrera seleccionada
            if ids_cursos:
                cursor.execute(
                    """
                    SELECT id_curso
                    FROM curso
                    WHERE id_curso = ANY(%s)
                      AND UPPER(TRIM(carrera)) =
                          UPPER(TRIM(%s))
                    """,
                    (
                        ids_cursos,
                        docente.especialidad
                    )
                )

                encontrados = {
                    fila["id_curso"]
                    for fila in cursor.fetchall()
                }

                if encontrados != set(ids_cursos):
                    raise ValueError(
                        "Uno o más cursos no pertenecen "
                        "a la carrera seleccionada."
                    )

            # Registrar docente
            cursor.execute(
                """
                INSERT INTO docente (
                    especialidad,
                    id_persona
                )
                VALUES (%s, %s)
                RETURNING id_docente
                """,
                (
                    docente.especialidad,
                    docente.id_persona
                )
            )

            fila = cursor.fetchone()
            docente.id_docente = fila["id_docente"]

            # Registrar sus cursos
            for id_curso in ids_cursos:
                cursor.execute(
                    """
                    INSERT INTO docente_curso (
                        id_docente,
                        id_curso
                    )
                    VALUES (%s, %s)
                    """,
                    (
                        docente.id_docente,
                        id_curso
                    )
                )

            # Confirmar ambas operaciones juntas
            conn.commit()

            return docente

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    # ==========================================
    # FILA A DOCENTE
    # ==========================================

    def __fila_a_docente(self, fila):
        return Docente(
            fila["id_docente"],
            fila["especialidad"],
            fila["id_persona"]
        )
