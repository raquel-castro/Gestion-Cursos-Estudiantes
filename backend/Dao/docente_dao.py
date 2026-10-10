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
                INSERT INTO docente
                (
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

            conn.commit()

            docente.id_docente = fila["id_docente"]

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

        cursor.execute(
            """
            SELECT *
            FROM docente
            WHERE id_docente = %s
            """,
            (
                docente_id,
            )
        )

        fila = cursor.fetchone()

        cursor.close()
        conn.close()

        return (
            self.__fila_a_docente(fila)
            if fila
            else None
        )


    # ==========================================
    # OBTENER TODOS
    # ==========================================

    def obtener_todos(self):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM docente
            ORDER BY especialidad
            """
        )

        filas = cursor.fetchall()

        cursor.close()
        conn.close()

        return [
            self.__fila_a_docente(fila)
            for fila in filas
        ]


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

            raise DocenteNoEncontradoError(
                docente_id
            )

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
                SET
                    especialidad = %s,
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
            f"Docente actualizado: "
            f"ID={docente_id}"
        )

        return d


    # ==========================================
    # ELIMINAR
    # ==========================================

    def eliminar(self, docente_id):

        d = self.buscar_por_id(docente_id)

        if not d:

            self.__log.error(
                f"Eliminar fallido: "
                f"Docente ID={docente_id} no existe"
            )

            raise DocenteNoEncontradoError(
                docente_id
            )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                DELETE FROM docente
                WHERE id_docente = %s
                """,
                (
                    docente_id,
                )
            )

            conn.commit()

        except psycopg2.IntegrityError:

            conn.rollback()

            self.__log.warning(
                f"Eliminar fallido: "
                f"Docente ID={docente_id} "
                f"tiene cursos asociados"
            )

            raise DocenteConCursosError(
                docente_id
            )

        finally:

            cursor.close()
            conn.close()

        self.__log.info(
            f"Docente eliminado: "
            f"ID={docente_id}"
        )


    # ==========================================
    # TOTAL
    # ==========================================


    def buscar(self, especialidad=None, nombre=None):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            condiciones = []
            valores = []
            if especialidad:
                condiciones.append("d.especialidad ILIKE %s")
                valores.append(f"%{especialidad.strip()}%")
            if nombre:
                condiciones.append("(p.nombres ILIKE %s OR p.apellidos ILIKE %s)")
                patron=f"%{nombre.strip()}%"
                valores.extend([patron, patron])
            if not condiciones:
                return []
            cursor.execute(
                f"""SELECT d.* FROM docente d
                    JOIN persona p ON p.id_persona = d.id_persona
                    WHERE {' AND '.join(condiciones)}
                    ORDER BY d.especialidad""",
                tuple(valores)
            )
            return [self.__fila_a_docente(fila) for fila in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def total(self):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM docente
            """
        )

        total = cursor.fetchone()["total"]

        cursor.close()
        conn.close()

        return total


    # ==========================================
    # FILA A DOCENTE
    # ==========================================

    def __fila_a_docente(self, fila):

        return Docente(
            fila["id_docente"],
            fila["especialidad"],
            fila["id_persona"]
        )
