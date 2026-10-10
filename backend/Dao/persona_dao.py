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
            self.__log.warning(f"DNI duplicado: {persona.dni}")
            raise DNIDuplicadoError(persona.dni)

        if persona.correo and self.buscar_por_correo(persona.correo):
            self.__log.warning(f"Correo duplicado: {persona.correo}")
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
                    telefono,
                    correo,
                    direccion
                )
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id_persona
                """,
                (
                    persona.dni,
                    persona.nombres,
                    persona.apellidos,
                    persona.telefono,
                    persona.correo,
                    persona.direccion
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

        return persona


    # ==========================================
    # BUSCAR POR DNI
    # ==========================================

    def buscar_por_dni(self, dni):

        conn = obtener_conexion()
        cursor = conn.cursor()

        cursor.execute(
            """
            SELECT *
            FROM persona
            WHERE dni = %s
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
            SELECT *
            FROM persona
            WHERE id_persona = %s
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
            SELECT *
            FROM persona
            ORDER BY nombres
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
        telefono=None,
        correo=None,
        direccion=None
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

        existente_dni = self.buscar_por_dni(nuevo_dni)
        if existente_dni and existente_dni.id_persona != persona_id:
            raise DNIDuplicadoError(nuevo_dni)

        if nuevo_correo:
            existente_correo = self.buscar_por_correo(nuevo_correo)
            if existente_correo and existente_correo.id_persona != persona_id:
                raise CorreoDuplicadoError(nuevo_correo)

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
                    telefono = %s,
                    correo = %s,
                    direccion = %s
                WHERE id_persona = %s
                """,
                (
                    nuevo_dni,
                    nuevo_nombre,
                    nuevo_apellido,
                    nuevo_telefono,
                    nuevo_correo,
                    nueva_direccion,
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

        p.dni = nuevo_dni
        p.nombres = nuevo_nombre
        p.apellidos = nuevo_apellido
        p.telefono = nuevo_telefono
        p.correo = nuevo_correo
        p.direccion = nueva_direccion

        self.__log.info(
            f"Persona actualizada: "
            f"{p.nombres} {p.apellidos} "
            f"(ID={persona_id})"
        )

        return p


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
    # TOTAL
    # ==========================================


    def buscar_por_correo(self, correo):
        if not correo:
            return None
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT * FROM persona WHERE LOWER(correo) = LOWER(%s)",
                (correo.strip(),)
            )
            fila = cursor.fetchone()
            return self.__fila_a_persona(fila) if fila else None
        finally:
            cursor.close()
            conn.close()

    def buscar(self, dni=None, nombre=None, apellido=None, correo=None):
        conn = obtener_conexion()
        cursor = conn.cursor()
        try:
            condiciones = []
            valores = []
            if dni:
                condiciones.append("dni = %s")
                valores.append(dni.strip())
            if nombre:
                condiciones.append("nombres ILIKE %s")
                valores.append(f"%{nombre.strip()}%")
            if apellido:
                condiciones.append("apellidos ILIKE %s")
                valores.append(f"%{apellido.strip()}%")
            if correo:
                condiciones.append("correo ILIKE %s")
                valores.append(f"%{correo.strip()}%")
            if not condiciones:
                return []
            cursor.execute(
                f"SELECT * FROM persona WHERE {' AND '.join(condiciones)} ORDER BY nombres, apellidos",
                tuple(valores)
            )
            return [self.__fila_a_persona(fila) for fila in cursor.fetchall()]
        finally:
            cursor.close()
            conn.close()

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
            fila["id_persona"],
            fila["dni"],
            fila["nombres"],
            fila["apellidos"],
            fila["telefono"],
            fila["correo"],
            fila["direccion"]
        )
