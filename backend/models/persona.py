from datetime import date


class Persona:

    def __init__(
        self,
        id_persona=0,
        dni="",
        nombres="",
        apellidos="",
        telefono="",
        correo="",
        direccion="",
        fecha_nacimiento=None,
        id_distrito=None,
        distrito=None
    ):

        self.__id_persona = id_persona
        self.__dni = dni
        self.__nombres = nombres
        self.__apellidos = apellidos
        self.__telefono = telefono
        self.__correo = correo
        self.__direccion = direccion
        self.__fecha_nacimiento = fecha_nacimiento
        self.__id_distrito = id_distrito
        self.__distrito = distrito

    @property
    def id_persona(self):
        return self.__id_persona

    @id_persona.setter
    def id_persona(self, valor):
        self.__id_persona = valor

    @property
    def dni(self):
        return self.__dni

    @dni.setter
    def dni(self, valor):
        self.__dni = valor

    @property
    def nombres(self):
        return self.__nombres

    @nombres.setter
    def nombres(self, valor):
        self.__nombres = valor

    @property
    def apellidos(self):
        return self.__apellidos

    @apellidos.setter
    def apellidos(self, valor):
        self.__apellidos = valor

    @property
    def telefono(self):
        return self.__telefono

    @telefono.setter
    def telefono(self, valor):
        self.__telefono = valor

    @property
    def correo(self):
        return self.__correo

    @correo.setter
    def correo(self, valor):
        self.__correo = valor

    @property
    def direccion(self):
        return self.__direccion

    @direccion.setter
    def direccion(self, valor):
        self.__direccion = valor

    @property
    def fecha_nacimiento(self):
        return self.__fecha_nacimiento

    @fecha_nacimiento.setter
    def fecha_nacimiento(self, valor):
        self.__fecha_nacimiento = valor

    @property
    def id_distrito(self):
        return self.__id_distrito

    @id_distrito.setter
    def id_distrito(self, valor):
        self.__id_distrito = valor

    @property
    def distrito(self):
        return self.__distrito

    @distrito.setter
    def distrito(self, valor):
        self.__distrito = valor

    @property
    def edad(self):
        if not self.__fecha_nacimiento:
            return None

        fecha = self.__fecha_nacimiento

        if isinstance(fecha, str):
            try:
                fecha = date.fromisoformat(fecha)
            except ValueError:
                return None

        hoy = date.today()

        return (
            hoy.year
            - fecha.year
            - (
                (hoy.month, hoy.day)
                < (fecha.month, fecha.day)
            )
        )

    def __str__(self):

        return (
            f"{self.__id_persona} - "
            f"{self.__dni} - "
            f"{self.__nombres} - "
            f"{self.__apellidos} - "
            f"{self.__correo} - "
            f"{self.__direccion} - "
            f"{self.__distrito}"
        )

    def to_dict(self):

        return {
            "id_persona": self.__id_persona,
            "dni": self.__dni,
            "nombres": self.__nombres,
            "apellidos": self.__apellidos,
            "fecha_nacimiento": self.__fecha_nacimiento,
            "edad": self.edad,
            "telefono": self.__telefono,
            "correo": self.__correo,
            "direccion": self.__direccion,
            "id_distrito": self.__id_distrito,
            "distrito": self.__distrito
        }

    @classmethod
    def from_dict(cls, datos):

        return cls(
            id_persona=datos.get("id_persona", 0),
            dni=datos.get("dni", ""),
            nombres=datos.get("nombres", ""),
            apellidos=datos.get("apellidos", ""),
            telefono=datos.get("telefono", ""),
            correo=datos.get("correo", ""),
            direccion=datos.get("direccion", ""),
            fecha_nacimiento=datos.get("fecha_nacimiento"),
            id_distrito=datos.get("id_distrito"),
            distrito=datos.get("distrito")
        )