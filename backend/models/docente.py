class Docente:

    def __init__(
        self,
        id_docente=0,
        especialidad="",
        id_persona=0
    ):

        self.__id_docente = id_docente
        self.__especialidad = especialidad
        self.__id_persona = id_persona

    @property
    def id_docente(self):
        return self.__id_docente

    @id_docente.setter
    def id_docente(self, valor):
        self.__id_docente = valor

    @property
    def especialidad(self):
        return self.__especialidad

    @especialidad.setter
    def especialidad(self, valor):
        self.__especialidad = valor

    @property
    def id_persona(self):
        return self.__id_persona

    @id_persona.setter
    def id_persona(self, valor):
        self.__id_persona = valor

    def __str__(self):

        return (
            f"{self.__id_docente} - "
            f"{self.__especialidad} - "
            f"{self.__id_persona}"
        )

    def to_dict(self):

        return {
            "id_docente": self.__id_docente,
            "especialidad": self.__especialidad,
            "id_persona": self.__id_persona
        }

    @classmethod
    def from_dict(cls, datos):

        return cls(
            datos.get("id_docente", 0),
            datos.get("especialidad", ""),
            datos.get("id_persona", 0)
        )
