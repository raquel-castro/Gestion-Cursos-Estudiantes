
import psycopg2

from config.logger import Logger
from config.base_datos import obtener_conexion
from models.curso import Curso


class CursoNoEncontradoError(Exception):
    def __init__(self, curso_id):
        super().__init__(f"Curso ID={curso_id} no encontrado")


class CursoDuplicadoError(Exception):
    def __init__(self, nombre):
        super().__init__(f"El curso '{nombre}' ya está registrado en esta carrera y ciclo")


class CursoConMatriculasError(Exception):
    def __init__(self, curso_id):
        super().__init__(
            f"Curso ID={curso_id} no se puede eliminar: "
            "tiene matrículas asociadas"
        )


class CursoDAO:

    def __init__(self):
        self.__log = Logger()

    def __fila_a_curso(self, fila):
        return Curso(
            fila["id_curso"],
            fila["nombre"],
            fila["descripcion"],
            fila["creditos"],
            fila["ciclo"],
            fila["horas_semanales"],
            fila["id_docente"],
            fila["carrera"]
        )

    def buscar_por_nombre(self, nombre, carrera=None, ciclo=None):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            consulta = """
                SELECT *
                FROM curso
                WHERE LOWER(TRIM(nombre)) = LOWER(TRIM(%s))
            """
            valores = [nombre]

            if carrera is not None:
                consulta += " AND UPPER(TRIM(carrera)) = UPPER(TRIM(%s))"
                valores.append(carrera)

            if ciclo is not None:
                consulta += " AND ciclo = %s"
                valores.append(ciclo)

            consulta += " ORDER BY id_curso LIMIT 1"

            cursor.execute(consulta, tuple(valores))
            fila = cursor.fetchone()

            return self.__fila_a_curso(fila) if fila else None

        finally:
            cursor.close()
            conn.close()

    def buscar_por_id(self, curso_id):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT * FROM curso WHERE id_curso = %s",
                (curso_id,)
            )
            fila = cursor.fetchone()
            return self.__fila_a_curso(fila) if fila else None

        finally:
            cursor.close()
            conn.close()

    def insertar(self, curso):
        if self.buscar(
            nombre_exacto=curso.nombre,
            carrera=curso.carrera,
            ciclo=curso.ciclo
        ):
            raise CursoDuplicadoError(curso.nombre)

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                INSERT INTO curso (
                    nombre,
                    descripcion,
                    creditos,
                    ciclo,
                    horas_semanales,
                    id_docente,
                    carrera
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                RETURNING id_curso
                """,
                (
                    curso.nombre,
                    curso.descripcion,
                    curso.creditos,
                    curso.ciclo,
                    curso.horas_semanales,
                    curso.id_docente,
                    curso.carrera
                )
            )

            fila = cursor.fetchone()
            curso.id_curso = fila["id_curso"]

            conn.commit()
            self.__log.info(
                f"Curso agregado: {curso.nombre} "
                f"(ID={curso.id_curso})"
            )
            return curso

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    def obtener_todos(self):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT *
                FROM curso
                ORDER BY carrera NULLS LAST,
                    CASE ciclo
                        WHEN 'I' THEN 1
                        WHEN 'II' THEN 2
                        WHEN 'III' THEN 3
                        WHEN 'IV' THEN 4
                        WHEN 'V' THEN 5
                        WHEN 'VI' THEN 6
                        ELSE 99
                    END,
                    nombre
                """
            )

            return [
                self.__fila_a_curso(fila)
                for fila in cursor.fetchall()
            ]

        finally:
            cursor.close()
            conn.close()

    def actualizar(
        self,
        curso_id,
        nombre=None,
        descripcion=None,
        creditos=None,
        ciclo=None,
        horas_semanales=None,
        id_docente=None,
        carrera=None
    ):
        curso = self.buscar_por_id(curso_id)

        if not curso:
            raise CursoNoEncontradoError(curso_id)

        nuevo_nombre = nombre if nombre is not None else curso.nombre
        nueva_descripcion = (
            descripcion if descripcion is not None
            else curso.descripcion
        )
        nuevos_creditos = (
            creditos if creditos is not None else curso.creditos
        )
        nuevo_ciclo = ciclo if ciclo is not None else curso.ciclo
        nuevas_horas = (
            horas_semanales if horas_semanales is not None
            else curso.horas_semanales
        )
        nuevo_docente = (
            id_docente if id_docente is not None
            else curso.id_docente
        )
        nueva_carrera = (
            carrera if carrera is not None else curso.carrera
        )

        duplicados = self.buscar(
            nombre_exacto=nuevo_nombre,
            carrera=nueva_carrera,
            ciclo=nuevo_ciclo
        )

        if any(c.id_curso != curso_id for c in duplicados):
            raise CursoDuplicadoError(nuevo_nombre)

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                UPDATE curso
                SET nombre = %s,
                    descripcion = %s,
                    creditos = %s,
                    ciclo = %s,
                    horas_semanales = %s,
                    id_docente = %s,
                    carrera = %s
                WHERE id_curso = %s
                """,
                (
                    nuevo_nombre,
                    nueva_descripcion,
                    nuevos_creditos,
                    nuevo_ciclo,
                    nuevas_horas,
                    nuevo_docente,
                    nueva_carrera,
                    curso_id
                )
            )

            conn.commit()

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

        curso.nombre = nuevo_nombre
        curso.descripcion = nueva_descripcion
        curso.creditos = nuevos_creditos
        curso.ciclo = nuevo_ciclo
        curso.horas_semanales = nuevas_horas
        curso.id_docente = nuevo_docente
        curso.carrera = nueva_carrera

        self.__log.info(f"Curso actualizado: ID={curso_id}")
        return curso

    def eliminar(self, curso_id):
        curso = self.buscar_por_id(curso_id)

        if not curso:
            raise CursoNoEncontradoError(curso_id)

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "DELETE FROM curso WHERE id_curso = %s",
                (curso_id,)
            )
            conn.commit()

        except psycopg2.IntegrityError:
            conn.rollback()
            raise CursoConMatriculasError(curso_id)

        finally:
            cursor.close()
            conn.close()

        self.__log.info(f"Curso eliminado: ID={curso_id}")

    def buscar(
        self,
        nombre=None,
        ciclo=None,
        id_docente=None,
        carrera=None,
        nombre_exacto=None
    ):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            condiciones = []
            valores = []

            if nombre:
                condiciones.append("nombre ILIKE %s")
                valores.append(f"%{nombre.strip()}%")

            if nombre_exacto:
                condiciones.append(
                    "LOWER(TRIM(nombre)) = LOWER(TRIM(%s))"
                )
                valores.append(nombre_exacto)

            if ciclo:
                condiciones.append("UPPER(ciclo) = UPPER(%s)")
                valores.append(ciclo.strip())

            if id_docente is not None:
                condiciones.append("id_docente = %s")
                valores.append(id_docente)

            if carrera:
                condiciones.append(
                    "UPPER(TRIM(carrera)) = UPPER(TRIM(%s))"
                )
                valores.append(carrera)

            if not condiciones:
                return []

            consulta = (
                "SELECT * FROM curso WHERE "
                + " AND ".join(condiciones)
                + " ORDER BY nombre"
            )

            cursor.execute(consulta, tuple(valores))

            return [
                self.__fila_a_curso(fila)
                for fila in cursor.fetchall()
            ]

        finally:
            cursor.close()
            conn.close()

    def total(self):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute("SELECT COUNT(*) AS total FROM curso")
            return cursor.fetchone()["total"]

        finally:
            cursor.close()
            conn.close()
