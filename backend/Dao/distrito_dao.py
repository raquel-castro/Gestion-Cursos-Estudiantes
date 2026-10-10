import psycopg2
from config.logger import Logger
from config.base_datos import obtener_conexion
from models.distrito import Distrito

# ==========================================
# EXCEPCIONES
# ==========================================

class DistritoNoEncontradoError(Exception):

    def __init__(self, distrito_id):

        super().__init__(
            f"Distrito ID={distrito_id} no encontrado"
        )


class DistritoDuplicadoError(Exception):

    def __init__(self, nombre):

        super().__init__(
            f"El distrito '{nombre}' ya está registrado"
        )


class DistritoConRegistrosError(Exception):

    def __init__(self, distrito_id):

        super().__init__(
            f"Distrito ID={distrito_id} no se puede eliminar: "
            f"tiene registros asociados"
        )


# ==========================================
# CLASE DISTRITO DAO
# ==========================================

class DistritoDAO:

    def __init__(self):

        self.__log = Logger()


    # ==========================================
    # INSERTAR
    # ==========================================

    def insertar(self, distrito):

        if self.buscar_por_nombre(distrito.nombre):

            self.__log.warning(
                f"Distrito duplicado: {distrito.nombre}"
            )

            raise DistritoDuplicadoError(
                distrito.nombre
            )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO distrito (nombre)
                VALUES (%s)
                RETURNING id_distrito
                """,
                (
                    distrito.nombre,
                )
            )

            fila = cursor.fetchone()

            conn.commit()

            distrito.id_distrito = fila["id_distrito"]

        except psycopg2.IntegrityError:

            conn.rollback()

            self.__log.warning(
                f"Distrito duplicado: {distrito.nombre}"
            )

            raise DistritoDuplicadoError(
                distrito.nombre
            )

        finally:

            cursor.close()
            conn.close()

        self.__log.info(
            f"Distrito agregado: {distrito.nombre} "
            f"(ID={distrito.id_distrito})"
        )

        return distrito


    # ==========================================
    # BUSCAR POR NOMBRE
    # ==========================================

    def buscar_por_nombre(self, nombre):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM distrito
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
            self.__fila_a_distrito(fila)
            if fila
            else None
        )


    # ==========================================
    # BUSCAR POR ID
    # ==========================================

    def buscar_por_id(self, distrito_id):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM distrito
            WHERE id_distrito = %s
            """,
            (
                distrito_id,
            )
        )

        fila = cursor.fetchone()

        cursor.close()
        conn.close()

        return (
            self.__fila_a_distrito(fila)
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
            FROM distrito
            ORDER BY nombre
            """
        )

        filas = cursor.fetchall()

        cursor.close()
        conn.close()

        return [
            self.__fila_a_distrito(fila)
            for fila in filas
        ]


    # ==========================================
    # ACTUALIZAR
    # ==========================================

    def actualizar(
        self,
        distrito_id,
        nombre=None
    ):

        d = self.buscar_por_id(distrito_id)

        if not d:

            self.__log.error(
                f"Actualizar fallido: "
                f"Distrito ID={distrito_id} no existe"
            )

            raise DistritoNoEncontradoError(
                distrito_id
            )

        nuevo_nombre = (
            nombre
            if nombre is not None
            else d.nombre
        )

        # Comprobar si el nuevo nombre
        # ya pertenece a otro distrito

        distrito_existente = self.buscar_por_nombre(
            nuevo_nombre
        )

        if (
            distrito_existente
            and distrito_existente.id_distrito != distrito_id
        ):

            self.__log.warning(
                f"Distrito duplicado: {nuevo_nombre}"
            )

            raise DistritoDuplicadoError(
                nuevo_nombre
            )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE distrito
                SET nombre = %s
                WHERE id_distrito = %s
                """,
                (
                    nuevo_nombre,
                    distrito_id
                )
            )

            conn.commit()

        except psycopg2.IntegrityError:

            conn.rollback()

            self.__log.warning(
                f"Actualizar fallido: "
                f"Distrito duplicado {nuevo_nombre}"
            )

            raise DistritoDuplicadoError(
                nuevo_nombre
            )

        finally:

            cursor.close()
            conn.close()

        d.nombre = nuevo_nombre

        self.__log.info(
            f"Distrito actualizado: "
            f"{d.nombre} (ID={distrito_id})"
        )

        return d


    # ==========================================
    # ELIMINAR
    # ==========================================

    def eliminar(self, distrito_id):

        d = self.buscar_por_id(distrito_id)

        if not d:

            self.__log.error(
                f"Eliminar fallido: "
                f"Distrito ID={distrito_id} no existe"
            )

            raise DistritoNoEncontradoError(
                distrito_id
            )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                DELETE FROM distrito
                WHERE id_distrito = %s
                """,
                (
                    distrito_id,
                )
            )

            conn.commit()

        except psycopg2.IntegrityError:

            conn.rollback()

            self.__log.warning(
                f"Eliminar fallido: "
                f"Distrito ID={distrito_id} "
                f"tiene registros asociados"
            )

            raise DistritoConRegistrosError(
                distrito_id
            )

        finally:

            cursor.close()
            conn.close()

        self.__log.info(
            f"Distrito eliminado: "
            f"{d.nombre} (ID={distrito_id})"
        )


    # ==========================================
    # TOTAL
    # ==========================================


    def buscar(self, nombre):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM distrito WHERE nombre ILIKE %s ORDER BY nombre",
                (f"%{nombre.strip()}%",)
            )
            return [self.__fila_a_distrito(fila) for fila in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

    def total(self):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM distrito
            """
        )

        total = cursor.fetchone()["total"]

        cursor.close()
        conn.close()

        return total


    # ==========================================
    # FILA A DISTRITO
    # ==========================================

    def __fila_a_distrito(self, fila):

        return Distrito(
            fila["id_distrito"],
            fila["nombre"]
        )
