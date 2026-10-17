
import psycopg2
from config.base_datos import obtener_conexion
from config.logger import Logger
from models.matricula import Matricula


class MatriculaNoEncontradaError(Exception):
    def __init__(self, matricula_id):
        super().__init__(
            f"Matrícula ID={matricula_id} no encontrada"
        )


class MatriculaDuplicadaError(Exception):
    def __init__(self, id_alumno, periodo):
        super().__init__(
            f"El alumno ID={id_alumno} ya tiene una "
            f"matrícula en el periodo {periodo}"
        )


class AlumnoNoEncontradoError(Exception):
    def __init__(self, id_alumno):
        super().__init__(
            f"Alumno ID={id_alumno} no encontrado"
        )


class DatosAlumnoIncompletosError(Exception):
    pass


class MatriculaDAO:

    def __init__(self):
        self.__log = Logger()

    def __fila_a_matricula(self, fila):
        return Matricula(
            id_matricula=fila["id_matricula"],
            fecha_matricula=fila["fecha_matricula"],
            estado=fila["estado"],
            id_alumno=fila["id_alumno"],
            id_curso=fila["id_curso"],
            carrera=fila["carrera"],
            turno=fila["turno"],
            ciclo=fila["ciclo"],
            periodo_academico=fila["periodo_academico"],
            condicion=fila["condicion"]
        )

    def obtener_todos(self):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT *
                    FROM matricula
                    ORDER BY fecha_matricula DESC, id_matricula DESC
                """)
                return [
                    self.__fila_a_matricula(fila)
                    for fila in cursor.fetchall()
                ]
        finally:
            conn.close()

    def buscar_por_id(self, matricula_id):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT *
                    FROM matricula
                    WHERE id_matricula = %s
                """, (matricula_id,))
                fila = cursor.fetchone()
                return self.__fila_a_matricula(fila) if fila else None
        finally:
            conn.close()

    def buscar(
        self,
        id_alumno=None,
        carrera=None,
        turno=None,
        ciclo=None,
        periodo_academico=None,
        condicion=None
    ):
        conn = obtener_conexion()
        try:
            condiciones = []
            valores = []

            filtros = {
                "id_alumno": id_alumno,
                "carrera": carrera,
                "turno": turno,
                "ciclo": ciclo,
                "periodo_academico": periodo_academico,
                "condicion": condicion
            }

            for campo, valor in filtros.items():
                if valor is not None:
                    condiciones.append(f"{campo} = %s")
                    valores.append(valor)

            consulta = "SELECT * FROM matricula"

            if condiciones:
                consulta += " WHERE " + " AND ".join(condiciones)

            consulta += " ORDER BY fecha_matricula DESC, id_matricula DESC"

            with conn.cursor() as cursor:
                cursor.execute(consulta, tuple(valores))
                return [
                    self.__fila_a_matricula(fila)
                    for fila in cursor.fetchall()
                ]
        finally:
            conn.close()

    def insertar(self, datos):
        conn = obtener_conexion()

        try:
            with conn.cursor() as cursor:

                # Obtener carrera y turno desde Alumnos.
                cursor.execute("""
                    SELECT carrera, turno_actual
                    FROM alumno
                    WHERE id_alumno = %s
                    FOR UPDATE
                """, (datos.id_alumno,))

                alumno = cursor.fetchone()

                if not alumno:
                    raise AlumnoNoEncontradoError(datos.id_alumno)

                carrera = alumno["carrera"]
                turno = alumno["turno_actual"]

                if not carrera or not turno:
                    raise DatosAlumnoIncompletosError(
                        "El alumno debe tener carrera y turno "
                        "registrados antes de matricularse."
                    )

                cursor.execute("""
                    INSERT INTO matricula (
                        id_alumno,
                        carrera,
                        turno,
                        ciclo,
                        periodo_academico,
                        condicion,
                        id_curso,
                        estado,
                        fecha_matricula
                    )
                    VALUES (
                        %s, %s, %s, %s, %s, %s,
                        NULL, 'ACTIVO', CURRENT_DATE
                    )
                    RETURNING *
                """, (
                    datos.id_alumno,
                    carrera,
                    turno,
                    datos.ciclo,
                    datos.periodo_academico,
                    datos.condicion
                ))

                fila = cursor.fetchone()

            conn.commit()
            self.__log.info(
                f"Matrícula registrada: ID={fila['id_matricula']}"
            )
            return self.__fila_a_matricula(fila)

        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            raise MatriculaDuplicadaError(
                datos.id_alumno,
                datos.periodo_academico
            )
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def actualizar(self, matricula_id, datos):
        conn = obtener_conexion()

        try:
            cambios = datos.model_dump(exclude_unset=True)

            if not cambios:
                return self.buscar_por_id(matricula_id)

            campos_permitidos = {
                "ciclo", "periodo_academico", "condicion"
            }

            campos = []
            valores = []

            for campo, valor in cambios.items():
                if campo in campos_permitidos:
                    campos.append(f"{campo} = %s")
                    valores.append(valor)

            valores.append(matricula_id)

            with conn.cursor() as cursor:
                cursor.execute(f"""
                    UPDATE matricula
                    SET {", ".join(campos)}
                    WHERE id_matricula = %s
                    RETURNING *
                """, tuple(valores))

                fila = cursor.fetchone()

                if not fila:
                    raise MatriculaNoEncontradaError(matricula_id)

            conn.commit()
            return self.__fila_a_matricula(fila)

        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            raise MatriculaDuplicadaError(
                "otro alumno o el mismo",
                "indicado"
            )
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def eliminar(self, matricula_id):
        conn = obtener_conexion()

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    DELETE FROM matricula
                    WHERE id_matricula = %s
                    RETURNING id_matricula
                """, (matricula_id,))

                if not cursor.fetchone():
                    raise MatriculaNoEncontradaError(matricula_id)

            conn.commit()
            self.__log.info(
                f"Matrícula eliminada: ID={matricula_id}"
            )

        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def total(self):
        conn = obtener_conexion()
        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*) AS total
                    FROM matricula
                """)
                return cursor.fetchone()["total"]
        finally:
            conn.close()
