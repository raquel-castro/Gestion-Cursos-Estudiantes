
import psycopg2

from config.logger import Logger
from config.base_datos import obtener_conexion
from models.alumno import Alumno


class AlumnoNoEncontradoError(Exception):
    def __init__(self, alumno_id):
        super().__init__(
            f"Alumno ID={alumno_id} no encontrado"
        )


class AlumnoConMatriculasError(Exception):
    def __init__(self, alumno_id):
        super().__init__(
            f"Alumno ID={alumno_id} tiene registros "
            f"relacionados y no se puede eliminar"
        )


class AlumnoDAO:

    def __init__(self):
        self.__log = Logger()

    # REGISTRAR ALUMNO
    def insertar(self, alumno):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT id_alumno
                FROM alumno
                WHERE id_persona = %s
                """,
                (alumno.id_persona,)
            )

            if cursor.fetchone():
                raise ValueError(
                    "Esta persona ya está registrada como alumno."
                )

            cursor.execute(
                """
                INSERT INTO alumno (
                    id_persona,
                    estado_academico,
                    carrera,
                    ciclo_ingreso,
                    fecha_ingreso,
                    fecha_termino,
                    turno_actual,
                    condicion_alumno
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_alumno
                """,
                (
                    alumno.id_persona,
                    alumno.estado_academico,
                    alumno.carrera,
                    alumno.ciclo_ingreso,
                    alumno.fecha_ingreso,
                    alumno.fecha_termino,
                    alumno.turno_actual,
                    alumno.condicion_alumno
                )
            )

            fila = cursor.fetchone()
            alumno.id_alumno = fila["id_alumno"]

            conn.commit()

            self.__log.info(
                f"Alumno registrado: ID={alumno.id_alumno}"
            )

            return alumno

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    # BUSCAR POR ID
    def buscar_por_id(self, alumno_id):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT *
                FROM alumno
                WHERE id_alumno = %s
                """,
                (alumno_id,)
            )

            fila = cursor.fetchone()

            return self.__fila_a_alumno(fila) if fila else None

        finally:
            cursor.close()
            conn.close()

    # BUSCAR POR DNI
    def buscar_por_dni(self, dni):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT a.*
                FROM alumno a
                INNER JOIN persona p
                    ON p.id_persona = a.id_persona
                WHERE p.dni = %s
                ORDER BY a.id_alumno
                """,
                (dni.strip(),)
            )

            return [
                self.__fila_a_alumno(fila)
                for fila in cursor.fetchall()
            ]

        finally:
            cursor.close()
            conn.close()

    # LISTAR TODOS
    def obtener_todos(self):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                SELECT a.*
                FROM alumno a
                INNER JOIN persona p
                    ON p.id_persona = a.id_persona
                ORDER BY
                    p.apellidos,
                    p.nombres,
                    a.id_alumno
                """
            )

            return [
                self.__fila_a_alumno(fila)
                for fila in cursor.fetchall()
            ]

        finally:
            cursor.close()
            conn.close()

    # ACTUALIZAR ALUMNO
    def actualizar(
        self,
        alumno_id,
        id_persona=None,
        estado_academico=None,
        carrera=None,
        ciclo_ingreso=None,
        fecha_ingreso=None,
        fecha_termino=None,
        turno_actual=None,
        condicion_alumno=None
    ):
        alumno = self.buscar_por_id(alumno_id)

        if not alumno:
            raise AlumnoNoEncontradoError(alumno_id)

        campos = {
            "id_persona": id_persona,
            "estado_academico": estado_academico,
            "carrera": carrera,
            "ciclo_ingreso": ciclo_ingreso,
            "fecha_ingreso": fecha_ingreso,
            "fecha_termino": fecha_termino,
            "turno_actual": turno_actual,
            "condicion_alumno": condicion_alumno
        }

        cambios = {
            clave: valor
            for clave, valor in campos.items()
            if valor is not None
        }

        if not cambios:
            return alumno

        asignaciones = ", ".join(
            f"{campo} = %s"
            for campo in cambios
        )

        valores = list(cambios.values())
        valores.append(alumno_id)

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                f"""
                UPDATE alumno
                SET {asignaciones}
                WHERE id_alumno = %s
                RETURNING *
                """,
                tuple(valores)
            )

            fila = cursor.fetchone()
            conn.commit()

            alumno_actualizado = self.__fila_a_alumno(fila)

            self.__log.info(
                f"Alumno actualizado: ID={alumno_id}"
            )

            return alumno_actualizado

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    # ELIMINAR ALUMNO
    def eliminar(self, alumno_id):
        alumno = self.buscar_por_id(alumno_id)

        if not alumno:
            raise AlumnoNoEncontradoError(alumno_id)

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                """
                DELETE FROM alumno
                WHERE id_alumno = %s
                """,
                (alumno_id,)
            )

            conn.commit()

            self.__log.info(
                f"Alumno eliminado: ID={alumno_id}"
            )

        except psycopg2.IntegrityError as ex:
            conn.rollback()

            raise AlumnoConMatriculasError(
                alumno_id
            ) from ex

        except Exception:
            conn.rollback()
            raise

        finally:
            cursor.close()
            conn.close()

    # BUSCAR POR DNI, NOMBRES Y APELLIDOS
    def buscar(
        self,
        dni=None,
        nombre=None,
        nombres=None,
        apellidos=None
    ):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            condiciones = []
            valores = []

            if dni and dni.strip():
                condiciones.append("p.dni = %s")
                valores.append(dni.strip())

            if nombres and nombres.strip():
                condiciones.append("p.nombres ILIKE %s")
                valores.append(f"%{nombres.strip()}%")

            if apellidos and apellidos.strip():
                condiciones.append("p.apellidos ILIKE %s")
                valores.append(f"%{apellidos.strip()}%")

            if nombre and nombre.strip():
                condiciones.append(
                    "("
                    "p.nombres ILIKE %s "
                    "OR p.apellidos ILIKE %s "
                    "OR CONCAT_WS(' ', p.nombres, p.apellidos) ILIKE %s"
                    ")"
                )

                patron = f"%{nombre.strip()}%"
                valores.extend([patron, patron, patron])

            if not condiciones:
                return []

            consulta = f"""
                SELECT a.*
                FROM alumno a
                INNER JOIN persona p
                    ON p.id_persona = a.id_persona
                WHERE {' AND '.join(condiciones)}
                ORDER BY
                    p.apellidos,
                    p.nombres,
                    a.id_alumno
            """

            cursor.execute(consulta, tuple(valores))

            return [
                self.__fila_a_alumno(fila)
                for fila in cursor.fetchall()
            ]

        finally:
            cursor.close()
            conn.close()

    # TOTAL DE ALUMNOS
    def total(self):
        conn = obtener_conexion()
        cursor = conn.cursor()

        try:
            cursor.execute(
                "SELECT COUNT(*) AS total FROM alumno"
            )

            return cursor.fetchone()["total"]

        finally:
            cursor.close()
            conn.close()

    # CONVERTIR FILA A OBJETO
    def __fila_a_alumno(self, fila):
        if fila is None:
            return None

        return Alumno(
            id_alumno=fila["id_alumno"],
            id_persona=fila["id_persona"],
            estado_academico=fila["estado_academico"],
            carrera=fila["carrera"],
            ciclo_ingreso=fila["ciclo_ingreso"],
            fecha_ingreso=fila["fecha_ingreso"],
            fecha_termino=fila["fecha_termino"],
            turno_actual=fila["turno_actual"],
            condicion_alumno=fila["condicion_alumno"]
        )
