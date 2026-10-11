import psycopg2

from config.logger import Logger
from config.base_datos import obtener_conexion
from models.persona import Persona


# ==========================================
# EXCEPCIONES
# ==========================================

class PersonaNoEncontradaError(Exception):

    def __init__(self, persona_id):
        super().__init__(
            f"Persona ID={persona_id} no encontrada"
        )


class DNIDuplicadoError(Exception):

    def __init__(self, dni):
        super().__init__(
            f"DNI '{dni}' ya registrado"
        )


class CorreoDuplicadoError(Exception):

    def __init__(self, correo):
        super().__init__(
            f"Correo '{correo}' ya registrado"
        )


class PersonaConRegistrosError(Exception):

    def __init__(self, persona_id):
        super().__init__(
            f"Persona ID={persona_id} no se puede eliminar: "
            f"tiene registros asociados"
        )


# ==========================================
# CLASE PERSONA DAO
# ==========================================

class PersonaDAO:

    def __init__(self):
        self.__log = Logger()

    # ==========================================
    # INSERTAR
    # ==========================================

    def insertar(self, persona):

        if self.buscar_por_dni(persona.dni):
            self.__log.warning(
                f"DNI duplicado: {persona.dni}"
            )
            raise DNIDuplicadoError(persona.dni)

        if persona.correo and self.buscar_por_correo(persona.correo):
            self.__log.warning(
                f"Correo duplicado: {persona.correo}"
            )
            raise CorreoDuplicadoError(persona.correo)

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                INSERT INTO persona
                (
                    dni,
                    nombres,
                    apellidos,
                    fecha_nacimiento,
                    telefono,
                    correo,
                    direccion,
                    id_distrito
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id_persona
                """,
                (
                    persona.dni,
                    persona.nombres,
                    persona.apellidos,
                    persona.fecha_nacimiento,
                    persona.telefono,
                    persona.correo,
                    persona.direccion,
                    persona.id_distrito
                )
            )

            fila = cursor.fetchone()

            conn.commit()

            persona.id_persona = fila["id_persona"]

        except psycopg2.IntegrityError as ex:

            conn.rollback()

            if "persona_dni_key" in str(ex):

                self.__log.warning(
                    f"DNI duplicado: {persona.dni}"
                )

                raise DNIDuplicadoError(
                    persona.dni
                )

            if "persona_correo_key" in str(ex):

                self.__log.warning(
                    f"Correo duplicado: {persona.correo}"
                )

                raise CorreoDuplicadoError(
                    persona.correo
                )

            raise

        finally:

            cursor.close()
            conn.close()

        self.__log.info(
            f"Persona agregada: "
            f"{persona.nombres} {persona.apellidos} "
            f"(ID={persona.id_persona})"
        )

        return self.buscar_por_id(persona.id_persona)

    # ==========================================
    # BUSCAR POR DNI
    # ==========================================

    def buscar_por_dni(self, dni):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                p.*,
                d.nombre AS distrito
            FROM persona p
            LEFT JOIN distrito d
                ON p.id_distrito = d.id_distrito
            WHERE p.dni = %s
            """,
            (
                dni,
            )
        )

        fila = cursor.fetchone()

        cursor.close()
        conn.close()

        return (
            self.__fila_a_persona(fila)
            if fila
            else None
        )

    # ==========================================
    # BUSCAR POR ID
    # ==========================================

    def buscar_por_id(self, persona_id):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT
                p.*,
                d.nombre AS distrito
            FROM persona p
            LEFT JOIN distrito d
                ON p.id_distrito = d.id_distrito
            WHERE p.id_persona = %s
            """,
            (
                persona_id,
            )
        )

        fila = cursor.fetchone()

        cursor.close()
        conn.close()

        return (
            self.__fila_a_persona(fila)
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
            SELECT
                p.*,
                d.nombre AS distrito
            FROM persona p
            LEFT JOIN distrito d
                ON p.id_distrito = d.id_distrito
            ORDER BY p.nombres, p.apellidos
            """
        )

        filas = cursor.fetchall()

        cursor.close()
        conn.close()

        return [
            self.__fila_a_persona(fila)
            for fila in filas
        ]

    # ==========================================
    # ACTUALIZAR
    # ==========================================

    def actualizar(
        self,
        persona_id,
        dni=None,
        nombres=None,
        apellidos=None,
        fecha_nacimiento=None,
        telefono=None,
        correo=None,
        direccion=None,
        id_distrito=None
    ):

        p = self.buscar_por_id(persona_id)

        if not p:

            self.__log.error(
                f"Actualizar fallido: "
                f"Persona ID={persona_id} no existe"
            )

            raise PersonaNoEncontradaError(
                persona_id
            )

        nuevo_dni = (
            dni
            if dni is not None
            else p.dni
        )

        nuevo_nombre = (
            nombres
            if nombres is not None
            else p.nombres
        )

        nuevo_apellido = (
            apellidos
            if apellidos is not None
            else p.apellidos
        )

        nueva_fecha_nacimiento = (
            fecha_nacimiento
            if fecha_nacimiento is not None
            else p.fecha_nacimiento
        )

        nuevo_telefono = (
            telefono
            if telefono is not None
            else p.telefono
        )

        nuevo_correo = (
            correo
            if correo is not None
            else p.correo
        )

        nueva_direccion = (
            direccion
            if direccion is not None
            else p.direccion
        )

        nuevo_id_distrito = (
            id_distrito
            if id_distrito is not None
            else p.id_distrito
        )

        existente_dni = self.buscar_por_dni(
            nuevo_dni
        )

        if (
            existente_dni
            and existente_dni.id_persona != persona_id
        ):
            raise DNIDuplicadoError(
                nuevo_dni
            )

        if nuevo_correo:

            existente_correo = self.buscar_por_correo(
                nuevo_correo
            )

            if (
                existente_correo
                and existente_correo.id_persona != persona_id
            ):
                raise CorreoDuplicadoError(
                    nuevo_correo
                )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                UPDATE persona
                SET
                    dni = %s,
                    nombres = %s,
                    apellidos = %s,
                    fecha_nacimiento = %s,
                    telefono = %s,
                    correo = %s,
                    direccion = %s,
                    id_distrito = %s
                WHERE id_persona = %s
                """,
                (
                    nuevo_dni,
                    nuevo_nombre,
                    nuevo_apellido,
                    nueva_fecha_nacimiento,
                    nuevo_telefono,
                    nuevo_correo,
                    nueva_direccion,
                    nuevo_id_distrito,
                    persona_id
                )
            )

            conn.commit()

        except psycopg2.IntegrityError as ex:

            conn.rollback()

            if "persona_dni_key" in str(ex):

                self.__log.warning(
                    f"DNI duplicado: {nuevo_dni}"
                )

                raise DNIDuplicadoError(
                    nuevo_dni
                )

            if "persona_correo_key" in str(ex):

                self.__log.warning(
                    f"Correo duplicado: {nuevo_correo}"
                )

                raise CorreoDuplicadoError(
                    nuevo_correo
                )

            raise

        finally:

            cursor.close()
            conn.close()

        self.__log.info(
            f"Persona actualizada: "
            f"{nuevo_nombre} {nuevo_apellido} "
            f"(ID={persona_id})"
        )

        return self.buscar_por_id(persona_id)

    # ==========================================
    # ELIMINAR
    # ==========================================

    def eliminar(self, persona_id):

        p = self.buscar_por_id(persona_id)

        if not p:

            self.__log.error(
                f"Eliminar fallido: "
                f"Persona ID={persona_id} no existe"
            )

            raise PersonaNoEncontradaError(
                persona_id
            )

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                DELETE FROM persona
                WHERE id_persona = %s
                """,
                (
                    persona_id,
                )
            )

            conn.commit()

        except psycopg2.IntegrityError:

            conn.rollback()

            self.__log.warning(
                f"Eliminar fallido: "
                f"Persona ID={persona_id} "
                f"tiene registros asociados"
            )

            raise PersonaConRegistrosError(
                persona_id
            )

        finally:

            cursor.close()
            conn.close()

        self.__log.info(
            f"Persona eliminada: "
            f"{p.nombres} {p.apellidos} "
            f"(ID={persona_id})"
        )

    # ==========================================
    # BUSCAR POR CORREO
    # ==========================================

    def buscar_por_correo(self, correo):

        if not correo:
            return None

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            cursor.execute(
                """
                SELECT
                    p.*,
                    d.nombre AS distrito
                FROM persona p
                LEFT JOIN distrito d
                    ON p.id_distrito = d.id_distrito
                WHERE LOWER(p.correo) = LOWER(%s)
                """,
                (
                    correo.strip(),
                )
            )

            fila = cursor.fetchone()

            return (
                self.__fila_a_persona(fila)
                if fila
                else None
            )

        finally:

            cursor.close()
            conn.close()

    # ==========================================
    # BUSCAR
    # ==========================================

    def buscar(
        self,
        dni=None,
        nombre=None,
        apellido=None
    ):

        conn = obtener_conexion()
        cursor = conn.cursor()

        try:

            condiciones = []
            valores = []

            if dni:
                condiciones.append(
                    "p.dni = %s"
                )
                valores.append(
                    dni.strip()
                )

            if nombre:
                condiciones.append(
                    "p.nombres ILIKE %s"
                )
                valores.append(
                    f"%{nombre.strip()}%"
                )

            if apellido:
                condiciones.append(
                    "p.apellidos ILIKE %s"
                )
                valores.append(
                    f"%{apellido.strip()}%"
                )

            if not condiciones:
                return []

            consulta = f"""
                SELECT
                    p.*,
                    d.nombre AS distrito
                FROM persona p
                LEFT JOIN distrito d
                    ON p.id_distrito = d.id_distrito
                WHERE {' AND '.join(condiciones)}
                ORDER BY p.nombres, p.apellidos
            """

            cursor.execute(
                consulta,
                tuple(valores)
            )

            return [
                self.__fila_a_persona(fila)
                for fila in cursor.fetchall()
            ]

        finally:

            cursor.close()
            conn.close()

    # ==========================================
    # TOTAL
    # ==========================================

    def total(self):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT COUNT(*) AS total
            FROM persona
            """
        )

        total = cursor.fetchone()["total"]

        cursor.close()
        conn.close()

        return total

    # ==========================================
    # FILA A PERSONA
    # ==========================================

    def __fila_a_persona(self, fila):

        return Persona(
            id_persona=fila["id_persona"],
            dni=fila["dni"],
            nombres=fila["nombres"],
            apellidos=fila["apellidos"],
            telefono=fila["telefono"],
            correo=fila["correo"],
            direccion=fila["direccion"],
            fecha_nacimiento=fila["fecha_nacimiento"],
            id_distrito=fila["id_distrito"],
            distrito=fila.get("distrito")
        )