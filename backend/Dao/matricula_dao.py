import psycopg2
from config.logger import Logger
from config.base_datos import obtener_conexion
from models.matricula import Matricula

# ==========================================
# EXCEPCIONES
# ==========================================

class MatriculaNoEncontradaError(Exception):

    def __init__(self, matricula_id):

        super().__init__(
            f"Matrícula ID={matricula_id} no encontrada"
        )


class MatriculaDuplicadaError(Exception):

    def __init__(self, id_alumno, id_curso):

        super().__init__(
            f"El alumno ID={id_alumno} "
            f"ya está matriculado en el curso ID={id_curso}"
        )


# ==========================================
# CLASE MATRICULA DAO
# ==========================================

class MatriculaDAO:

    def __init__(self):

        self.__log = Logger()


    # ==========================================
    # INSERTAR
    # ==========================================

    def insertar(self, matricula):

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            # Verificar matrícula duplicada

            cursor.execute(
                """
                SELECT id_matricula
                FROM matricula
                WHERE id_alumno = %s
                AND id_curso = %s
                """,
                (
                    matricula.id_alumno,
                    matricula.id_curso
                )
            )

            if cursor.fetchone():

                self.__log.warning(
                    f"Matrícula duplicada: "
                    f"Alumno={matricula.id_alumno}, "
                    f"Curso={matricula.id_curso}"
                )

                raise MatriculaDuplicadaError(
                    matricula.id_alumno,
                    matricula.id_curso
                )

            cursor.execute(
                """
                INSERT INTO matricula
                (
                    fecha_matricula,
                    estado,
                    id_alumno,
                    id_curso
                )
                VALUES (%s, %s, %s, %s)
                RETURNING id_matricula
                """,
                (
                    matricula.fecha_matricula,
                    matricula.estado.upper(),
                    matricula.id_alumno,
                    matricula.id_curso
                )
            )

            fila = cursor.fetchone()

            conn.commit()

            matricula.id_matricula = fila["id_matricula"]
            matricula.estado = matricula.estado.upper()

        except psycopg2.IntegrityError as ex:

            conn.rollback()

            self.__log.warning(
                f"Error al insertar matrícula: "
                f"Alumno={matricula.id_alumno}, "
                f"Curso={matricula.id_curso}"
            )

            raise ex

        finally:

            cursor.close()
            conn.close()

        self.__log.info(
            f"Matrícula agregada: "
            f"ID={matricula.id_matricula}"
        )

        return matricula


    # ==========================================
    # BUSCAR POR ID
    # ==========================================

    def buscar_por_id(self, matricula_id):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM matricula
            WHERE id_matricula = %s
            """,
            (
                matricula_id,
            )
        )

        fila = cursor.fetchone()

        cursor.close()
        conn.close()

        return (
            self.__fila_a_matricula(fila)
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
            FROM matricula
            ORDER BY fecha_matricula
            """
        )

        filas = cursor.fetchall()

        cursor.close()
        conn.close()

        return [
            self.__fila_a_matricula(fila)
            for fila in filas
        ]


    # ==========================================
    # ACTUALIZAR
    # ==========================================

    def actualizar(
        self,
        matricula_id,
        fecha_matricula=None,
        estado=None,
        id_alumno=None,
        id_curso=None
    ):

        m = self.buscar_por_id(matricula_id)

        if not m:

            self.__log.error(
                f"Actualizar fallido: "
                f"Matrícula ID={matricula_id} "
                f"no existe"
            )

            raise MatriculaNoEncontradaError(
                matricula_id
            )

        nueva_fecha = (
            fecha_matricula
            if fecha_matricula is not None
            else m.fecha_matricula
        )

        nuevo_estado = (
            estado.upper()
            if estado is not None
            else m.estado
        )

        nuevo_alumno = (
            id_alumno
            if id_alumno is not None
            else m.id_alumno
        )

        nuevo_curso = (
            id_curso
            if id_curso is not None
            else m.id_curso
        )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            # Verificar si el cambio genera una matrícula
            # duplicada

            cursor.execute(
                """
                SELECT id_matricula
                FROM matricula
                WHERE id_alumno = %s
                AND id_curso = %s
                AND id_matricula <> %s
                """,
                (
                    nuevo_alumno,
                    nuevo_curso,
                    matricula_id
                )
            )

            if cursor.fetchone():

                self.__log.warning(
                    f"Actualizar fallido: "
                    f"Alumno={nuevo_alumno}, "
                    f"Curso={nuevo_curso} "
                    f"ya están matriculados"
                )

                raise MatriculaDuplicadaError(
                    nuevo_alumno,
                    nuevo_curso
                )

            cursor.execute(
                """
                UPDATE matricula
                SET
                    fecha_matricula = %s,
                    estado = %s,
                    id_alumno = %s,
                    id_curso = %s
                WHERE id_matricula = %s
                """,
                (
                    nueva_fecha,
                    nuevo_estado,
                    nuevo_alumno,
                    nuevo_curso,
                    matricula_id
                )
            )

            conn.commit()

        except psycopg2.IntegrityError:

            conn.rollback()

            self.__log.warning(
                f"Actualizar fallido: "
                f"Matrícula ID={matricula_id}"
            )

            raise

        finally:

            cursor.close()
            conn.close()

        m.fecha_matricula = nueva_fecha
        m.estado = nuevo_estado
        m.id_alumno = nuevo_alumno
        m.id_curso = nuevo_curso

        self.__log.info(
            f"Matrícula actualizada: "
            f"ID={matricula_id}"
        )

        return m


    # ==========================================
    # ELIMINAR
    # ==========================================

    def eliminar(self, matricula_id):

        m = self.buscar_por_id(matricula_id)

        if not m:

            self.__log.error(
                f"Eliminar fallido: "
                f"Matrícula ID={matricula_id} "
                f"no existe"
            )

            raise MatriculaNoEncontradaError(
                matricula_id
            )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                DELETE FROM matricula
                WHERE id_matricula = %s
                """,
                (
                    matricula_id,
                )
            )

            conn.commit()

        except psycopg2.IntegrityError:

            conn.rollback()

            raise

        finally:

            cursor.close()
            conn.close()

        self.__log.info(
            f"Matrícula eliminada: "
            f"ID={matricula_id}"
        )


    # ==========================================
    # TOTAL
    # ==========================================


    def buscar(self, id_alumno=None, id_curso=None, estado=None):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            condiciones = []
            valores = []
            if id_alumno is not None:
                condiciones.append("id_alumno = %s")
                valores.append(id_alumno)
            if id_curso is not None:
                condiciones.append("id_curso = %s")
                valores.append(id_curso)
            if estado:
                condiciones.append("UPPER(estado) = UPPER(%s)")
                valores.append(estado.strip())
            if not condiciones:
                return []
            cursor.execute(
                f"SELECT * FROM matricula WHERE {' AND '.join(condiciones)} ORDER BY fecha_matricula, id_matricula",
                tuple(valores)
            )
            return [self.__fila_a_matricula(fila) for fila in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def total(self):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM matricula
            """
        )

        total = cursor.fetchone()["total"]

        cursor.close()
        conn.close()

        return total


    # ==========================================
    # FILA A MATRICULA
    # ==========================================

    def __fila_a_matricula(self, fila):

        return Matricula(
            fila["id_matricula"],
            fila["fecha_matricula"],
            fila["estado"],
            fila["id_alumno"],
            fila["id_curso"]
        )
