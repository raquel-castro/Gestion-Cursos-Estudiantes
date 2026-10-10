import psycopg2
from config.logger import Logger
from config.base_datos import obtener_conexion
from models.alumno import Alumno

# ==========================================
# EXCEPCIONES
# ==========================================

class AlumnoNoEncontradoError(Exception):

    def __init__(self, alumno_id):

        super().__init__(
            f"Alumno ID={alumno_id} no encontrado"
        )


class CodigoAlumnoDuplicadoError(Exception):

    def __init__(self, codigo):

        super().__init__(
            f"Código '{codigo}' ya registrado"
        )


class AlumnoConMatriculasError(Exception):

    def __init__(self, alumno_id):

        super().__init__(
            f"Alumno ID={alumno_id} no se puede eliminar: "
            f"tiene matrículas asociadas"
        )


# ==========================================
# CLASE ALUMNO DAO
# ==========================================

class AlumnoDAO:

    def __init__(self):

        self.__log = Logger()


    # ==========================================
    # INSERTAR
    # ==========================================

    def insertar(self, alumno):

        if self.buscar_por_codigo(
            alumno.codigo_alumno
        ):

            self.__log.warning(
                f"Código duplicado: "
                f"{alumno.codigo_alumno}"
            )

            raise CodigoAlumnoDuplicadoError(
                alumno.codigo_alumno
            )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO alumno
                (
                    codigo_alumno,
                    id_persona,
                    id_distrito
                )
                VALUES (%s, %s, %s)
                RETURNING id_alumno
                """,
                (
                    alumno.codigo_alumno,
                    alumno.id_persona,
                    alumno.id_distrito
                )
            )

            fila = cursor.fetchone()

            conn.commit()

            alumno.id_alumno = fila["id_alumno"]

        except psycopg2.IntegrityError as ex:

            conn.rollback()

            if "alumno_codigo_alumno_key" in str(ex):

                self.__log.warning(
                    f"Código duplicado: "
                    f"{alumno.codigo_alumno}"
                )

                raise CodigoAlumnoDuplicadoError(
                    alumno.codigo_alumno
                )

            raise

        finally:

            cursor.close()
            conn.close()

        self.__log.info(
            f"Alumno agregado: "
            f"{alumno.codigo_alumno} "
            f"(ID={alumno.id_alumno})"
        )

        return alumno


    # ==========================================
    # BUSCAR POR CÓDIGO
    # ==========================================

    def buscar_por_codigo(self, codigo):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM alumno
            WHERE codigo_alumno = %s
            """,
            (
                codigo,
            )
        )

        fila = cursor.fetchone()

        cursor.close()
        conn.close()

        return (
            self.__fila_a_alumno(fila)
            if fila
            else None
        )


    # ==========================================
    # BUSCAR POR ID
    # ==========================================

    def buscar_por_id(self, alumno_id):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM alumno
            WHERE id_alumno = %s
            """,
            (
                alumno_id,
            )
        )

        fila = cursor.fetchone()

        cursor.close()
        conn.close()

        return (
            self.__fila_a_alumno(fila)
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
            FROM alumno
            ORDER BY codigo_alumno
            """
        )

        filas = cursor.fetchall()

        cursor.close()
        conn.close()

        return [
            self.__fila_a_alumno(fila)
            for fila in filas
        ]


    # ==========================================
    # ACTUALIZAR
    # ==========================================

    def actualizar(
        self,
        alumno_id,
        codigo_alumno=None,
        id_persona=None,
        id_distrito=None
    ):

        a = self.buscar_por_id(alumno_id)

        if not a:

            self.__log.error(
                f"Actualizar fallido: "
                f"Alumno ID={alumno_id} no existe"
            )

            raise AlumnoNoEncontradoError(
                alumno_id
            )

        nuevo_codigo = (
            codigo_alumno
            if codigo_alumno is not None
            else a.codigo_alumno
        )

        nueva_persona = (
            id_persona
            if id_persona is not None
            else a.id_persona
        )

        nuevo_distrito = (
            id_distrito
            if id_distrito is not None
            else a.id_distrito
        )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE alumno
                SET
                    codigo_alumno = %s,
                    id_persona = %s,
                    id_distrito = %s
                WHERE id_alumno = %s
                """,
                (
                    nuevo_codigo,
                    nueva_persona,
                    nuevo_distrito,
                    alumno_id
                )
            )

            conn.commit()

        except psycopg2.IntegrityError as ex:

            conn.rollback()

            if "alumno_codigo_alumno_key" in str(ex):

                self.__log.warning(
                    f"Actualizar fallido: "
                    f"Código '{nuevo_codigo}' ya registrado"
                )

                raise CodigoAlumnoDuplicadoError(
                    nuevo_codigo
                )

            raise

        finally:

            cursor.close()
            conn.close()

        a.codigo_alumno = nuevo_codigo
        a.id_persona = nueva_persona
        a.id_distrito = nuevo_distrito

        self.__log.info(
            f"Alumno actualizado: "
            f"ID={alumno_id}"
        )

        return a


    # ==========================================
    # ELIMINAR
    # ==========================================

    def eliminar(self, alumno_id):

        a = self.buscar_por_id(alumno_id)

        if not a:

            self.__log.error(
                f"Eliminar fallido: "
                f"Alumno ID={alumno_id} no existe"
            )

            raise AlumnoNoEncontradoError(
                alumno_id
            )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                DELETE FROM alumno
                WHERE id_alumno = %s
                """,
                (
                    alumno_id,
                )
            )

            conn.commit()

        except psycopg2.IntegrityError:

            conn.rollback()

            self.__log.warning(
                f"Eliminar fallido: "
                f"Alumno ID={alumno_id} "
                f"tiene matrículas asociadas"
            )

            raise AlumnoConMatriculasError(
                alumno_id
            )

        finally:

            cursor.close()
            conn.close()

        self.__log.info(
            f"Alumno eliminado: "
            f"ID={alumno_id}"
        )


    # ==========================================
    # TOTAL
    # ==========================================


    def buscar(self, codigo=None, dni=None, nombre=None, distrito=None):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            condiciones = []
            valores = []
            if codigo:
                condiciones.append("a.codigo_alumno ILIKE %s")
                valores.append(f"%{codigo.strip()}%")
            if dni:
                condiciones.append("p.dni = %s")
                valores.append(dni.strip())
            if nombre:
                condiciones.append("(p.nombres ILIKE %s OR p.apellidos ILIKE %s)")
                patron=f"%{nombre.strip()}%"
                valores.extend([patron, patron])
            if distrito:
                condiciones.append("d.nombre ILIKE %s")
                valores.append(f"%{distrito.strip()}%")
            if not condiciones:
                return []
            cursor.execute(
                f"""SELECT a.* FROM alumno a
                    JOIN persona p ON p.id_persona = a.id_persona
                    JOIN distrito d ON d.id_distrito = a.id_distrito
                    WHERE {' AND '.join(condiciones)}
                    ORDER BY a.codigo_alumno""",
                tuple(valores)
            )
            return [self.__fila_a_alumno(fila) for fila in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def total(self):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM alumno
            """
        )

        total = cursor.fetchone()["total"]

        cursor.close()
        conn.close()

        return total


    # ==========================================
    # FILA A ALUMNO
    # ==========================================

    def __fila_a_alumno(self, fila):

        return Alumno(
            fila["id_alumno"],
            fila["codigo_alumno"],
            fila["id_persona"],
            fila["id_distrito"]
        )
