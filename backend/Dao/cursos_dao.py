import psycopg2
from config.logger import Logger
from config.base_datos import obtener_conexion
from models.curso import Curso

# ==========================================
# EXCEPCIONES
# ==========================================

class CursoNoEncontradoError(Exception):

    def __init__(self, curso_id):

        super().__init__(
            f"Curso ID={curso_id} no encontrado"
        )


class CursoDuplicadoError(Exception):

    def __init__(self, nombre):

        super().__init__(
            f"El curso '{nombre}' ya está registrado"
        )


class CursoConMatriculasError(Exception):

    def __init__(self, curso_id):

        super().__init__(
            f"Curso ID={curso_id} no se puede eliminar: "
            f"tiene matrículas asociadas"
        )


# ==========================================
# CLASE CURSO DAO
# ==========================================

class CursoDAO:

    def __init__(self):

        self.__log = Logger()


    # ==========================================
    # INSERTAR
    # ==========================================

    def insertar(self, curso):

        if self.buscar_por_nombre(curso.nombre):

            self.__log.warning(
                f"Curso duplicado: {curso.nombre}"
            )

            raise CursoDuplicadoError(
                curso.nombre
            )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO curso
                (
                    nombre,
                    descripcion,
                    creditos,
                    ciclo,
                    horas_semanales,
                    id_docente
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_curso
                """,
                (
                    curso.nombre,
                    curso.descripcion,
                    curso.creditos,
                    curso.ciclo,
                    curso.horas_semanales,
                    curso.id_docente
                )
            )

            fila = cursor.fetchone()

            conn.commit()

            curso.id_curso = fila["id_curso"]

        except psycopg2.IntegrityError as ex:

            conn.rollback()

            if "curso_nombre_key" in str(ex):

                self.__log.warning(
                    f"Curso duplicado: "
                    f"{curso.nombre}"
                )

                raise CursoDuplicadoError(
                    curso.nombre
                )

            raise

        finally:

            cursor.close()
            conn.close()

        self.__log.info(
            f"Curso agregado: "
            f"{curso.nombre} "
            f"(ID={curso.id_curso})"
        )

        return curso


    # ==========================================
    # BUSCAR POR NOMBRE
    # ==========================================

    def buscar_por_nombre(self, nombre):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM curso
            WHERE UPPER(nombre) = UPPER(%s)
            """,
            (
                nombre,
            )
        )

        fila = cursor.fetchone()

        cursor.close()
        conn.close()

        return (
            self.__fila_a_curso(fila)
            if fila
            else None
        )


    # ==========================================
    # BUSCAR POR ID
    # ==========================================

    def buscar_por_id(self, curso_id):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM curso
            WHERE id_curso = %s
            """,
            (
                curso_id,
            )
        )

        fila = cursor.fetchone()

        cursor.close()
        conn.close()

        return (
            self.__fila_a_curso(fila)
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
            FROM curso
            ORDER BY nombre
            """
        )

        filas = cursor.fetchall()

        cursor.close()
        conn.close()

        return [
            self.__fila_a_curso(fila)
            for fila in filas
        ]


    # ==========================================
    # ACTUALIZAR
    # ==========================================

    def actualizar(
        self,
        curso_id,
        nombre=None,
        descripcion=None,
        creditos=None,
        ciclo=None,
        horas_semanales=None,
        id_docente=None
    ):

        c = self.buscar_por_id(curso_id)

        if not c:

            self.__log.error(
                f"Actualizar fallido: "
                f"Curso ID={curso_id} no existe"
            )

            raise CursoNoEncontradoError(
                curso_id
            )

        nuevo_nombre = (
            nombre
            if nombre is not None
            else c.nombre
        )

        nueva_descripcion = (
            descripcion
            if descripcion is not None
            else c.descripcion
        )

        nuevos_creditos = (
            creditos
            if creditos is not None
            else c.creditos
        )

        nuevo_ciclo = (
            ciclo
            if ciclo is not None
            else c.ciclo
        )

        nuevas_horas = (
            horas_semanales
            if horas_semanales is not None
            else c.horas_semanales
        )

        nuevo_docente = (
            id_docente
            if id_docente is not None
            else c.id_docente
        )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE curso
                SET
                    nombre = %s,
                    descripcion = %s,
                    creditos = %s,
                    ciclo = %s,
                    horas_semanales = %s,
                    id_docente = %s
                WHERE id_curso = %s
                """,
                (
                    nuevo_nombre,
                    nueva_descripcion,
                    nuevos_creditos,
                    nuevo_ciclo,
                    nuevas_horas,
                    nuevo_docente,
                    curso_id
                )
            )

            conn.commit()

        except psycopg2.IntegrityError as ex:

            conn.rollback()

            if "curso_nombre_key" in str(ex):

                self.__log.warning(
                    f"Actualizar fallido: "
                    f"Curso duplicado "
                    f"{nuevo_nombre}"
                )

                raise CursoDuplicadoError(
                    nuevo_nombre
                )

            raise

        finally:

            cursor.close()
            conn.close()

        c.nombre = nuevo_nombre
        c.descripcion = nueva_descripcion
        c.creditos = nuevos_creditos
        c.ciclo = nuevo_ciclo
        c.horas_semanales = nuevas_horas
        c.id_docente = nuevo_docente

        self.__log.info(
            f"Curso actualizado: "
            f"{c.nombre} "
            f"(ID={curso_id})"
        )

        return c


    # ==========================================
    # ELIMINAR
    # ==========================================

    def eliminar(self, curso_id):

        c = self.buscar_por_id(curso_id)

        if not c:

            self.__log.error(
                f"Eliminar fallido: "
                f"Curso ID={curso_id} no existe"
            )

            raise CursoNoEncontradoError(
                curso_id
            )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                DELETE FROM curso
                WHERE id_curso = %s
                """,
                (
                    curso_id,
                )
            )

            conn.commit()

        except psycopg2.IntegrityError:

            conn.rollback()

            self.__log.warning(
                f"Eliminar fallido: "
                f"Curso ID={curso_id} "
                f"tiene matrículas asociadas"
            )

            raise CursoConMatriculasError(
                curso_id
            )

        finally:

            cursor.close()
            conn.close()

        self.__log.info(
            f"Curso eliminado: "
            f"{c.nombre} "
            f"(ID={curso_id})"
        )


    # ==========================================
    # TOTAL
    # ==========================================


    def buscar(self, nombre=None, ciclo=None, id_docente=None):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            condiciones = []
            valores = []
            if nombre:
                condiciones.append("nombre ILIKE %s")
                valores.append(f"%{nombre.strip()}%")
            if ciclo:
                condiciones.append("UPPER(ciclo) = UPPER(%s)")
                valores.append(ciclo.strip())
            if id_docente is not None:
                condiciones.append("id_docente = %s")
                valores.append(id_docente)
            if not condiciones:
                return []
            cursor.execute(
                f"SELECT * FROM curso WHERE {' AND '.join(condiciones)} ORDER BY nombre",
                tuple(valores)
            )
            return [self.__fila_a_curso(fila) for fila in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def total(self):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM curso
            """
        )

        total = cursor.fetchone()["total"]

        cursor.close()
        conn.close()

        return total


    # ==========================================
    # FILA A CURSO
    # ==========================================

    def __fila_a_curso(self, fila):

        return Curso(
            fila["id_curso"],
            fila["nombre"],
            fila["descripcion"],
            fila["creditos"],
            fila["ciclo"],
            fila["horas_semanales"],
            fila["id_docente"]
        )
