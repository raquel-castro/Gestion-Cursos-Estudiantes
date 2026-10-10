class Distrito:

    def __init__(self, id_distrito=0, nombre=""):

        self.__id_distrito = id_distrito
        self.__nombre = nombre

    @property
    def id_distrito(self):
        return self.__id_distrito

    @id_distrito.setter
    def id_distrito(self, valor):
        self.__id_distrito = valor

    @property
    def nombre(self):
        return self.__nombre

    @nombre.setter
    def nombre(self, valor):
        self.__nombre = valor

    def __str__(self):

        return f"{self.__id_distrito} - {self.__nombre}"

    def to_dict(self):

        return {
            "id_distrito": self.__id_distrito,
            "nombre": self.__nombre
        }

    @classmethod
    def from_dict(cls, datos):

        return cls(
            datos.get("id_distrito", 0),
            datos.get("nombre", "")
        )
