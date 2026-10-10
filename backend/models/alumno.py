class Alumno:

    def __init__(
        self,
        id_alumno=0,
        codigo_alumno="",
        id_persona=0,
        id_distrito=0
    ):

        self.__id_alumno = id_alumno
        self.__codigo_alumno = codigo_alumno
        self.__id_persona = id_persona
        self.__id_distrito = id_distrito

    @property
    def id_alumno(self):
        return self.__id_alumno

    @id_alumno.setter
    def id_alumno(self, valor):
        self.__id_alumno = valor

    @property
    def codigo_alumno(self):
        return self.__codigo_alumno

    @codigo_alumno.setter
    def codigo_alumno(self, valor):
        self.__codigo_alumno = valor

    @property
    def id_persona(self):
        return self.__id_persona

    @id_persona.setter
    def id_persona(self, valor):
        self.__id_persona = valor

    @property
    def id_distrito(self):
        return self.__id_distrito

    @id_distrito.setter
    def id_distrito(self, valor):
        self.__id_distrito = valor

    def __str__(self):

        return (
            f"ID:{self.__id_alumno} | "
            f"Código:{self.__codigo_alumno} | "
            f"Persona:{self.__id_persona} | "
            f"Distrito:{self.__id_distrito}"
        )

    def to_dict(self):

        return {
            "id_alumno": self.__id_alumno,
            "codigo_alumno": self.__codigo_alumno,
            "id_persona": self.__id_persona,
            "id_distrito": self.__id_distrito
        }

    @classmethod
    def from_dict(cls, datos):

        return cls(
            datos.get("id_alumno", 0),
            datos.get("codigo_alumno", ""),
            datos.get("id_persona", 0),
            datos.get("id_distrito", 0)
        )
