
class Alumno:

    def __init__(
        self,
        id_alumno=0,
        id_persona=0,
        estado_academico=None,
        carrera=None,
        ciclo_ingreso=None,
        fecha_ingreso=None,
        fecha_termino=None,
        turno_actual=None,
        condicion_alumno=None
    ):
        self.__id_alumno = id_alumno
        self.__id_persona = id_persona
        self.__estado_academico = estado_academico
        self.__carrera = carrera
        self.__ciclo_ingreso = ciclo_ingreso
        self.__fecha_ingreso = fecha_ingreso
        self.__fecha_termino = fecha_termino
        self.__turno_actual = turno_actual
        self.__condicion_alumno = condicion_alumno

    @property
    def id_alumno(self):
        return self.__id_alumno

    @id_alumno.setter
    def id_alumno(self, valor):
        self.__id_alumno = valor

    @property
    def id_persona(self):
        return self.__id_persona

    @id_persona.setter
    def id_persona(self, valor):
        self.__id_persona = valor

    @property
    def estado_academico(self):
        return self.__estado_academico

    @estado_academico.setter
    def estado_academico(self, valor):
        self.__estado_academico = valor

    @property
    def carrera(self):
        return self.__carrera

    @carrera.setter
    def carrera(self, valor):
        self.__carrera = valor

    @property
    def ciclo_ingreso(self):
        return self.__ciclo_ingreso

    @ciclo_ingreso.setter
    def ciclo_ingreso(self, valor):
        self.__ciclo_ingreso = valor

    @property
    def fecha_ingreso(self):
        return self.__fecha_ingreso

    @fecha_ingreso.setter
    def fecha_ingreso(self, valor):
        self.__fecha_ingreso = valor

    @property
    def fecha_termino(self):
        return self.__fecha_termino

    @fecha_termino.setter
    def fecha_termino(self, valor):
        self.__fecha_termino = valor

    @property
    def turno_actual(self):
        return self.__turno_actual

    @turno_actual.setter
    def turno_actual(self, valor):
        self.__turno_actual = valor

    @property
    def condicion_alumno(self):
        return self.__condicion_alumno

    @condicion_alumno.setter
    def condicion_alumno(self, valor):
        self.__condicion_alumno = valor

    def __str__(self):
        return (
            f"ID Alumno: {self.__id_alumno} | "
            f"ID Persona: {self.__id_persona} | "
            f"Carrera: {self.__carrera} | "
            f"Ciclo de ingreso: {self.__ciclo_ingreso} | "
            f"Turno: {self.__turno_actual} | "
            f"Condición: {self.__condicion_alumno}"
        )

    def to_dict(self):
        return {
            "id_alumno": self.__id_alumno,
            "id_persona": self.__id_persona,
            "estado_academico": self.__estado_academico,
            "carrera": self.__carrera,
            "ciclo_ingreso": self.__ciclo_ingreso,
            "fecha_ingreso": self.__fecha_ingreso,
            "fecha_termino": self.__fecha_termino,
            "turno_actual": self.__turno_actual,
            "condicion_alumno": self.__condicion_alumno
        }

    @classmethod
    def from_dict(cls, datos):
        return cls(
            id_alumno=datos.get("id_alumno", 0),
            id_persona=datos.get("id_persona", 0),
            estado_academico=datos.get("estado_academico"),
            carrera=datos.get("carrera"),
            ciclo_ingreso=datos.get("ciclo_ingreso"),
            fecha_ingreso=datos.get("fecha_ingreso"),
            fecha_termino=datos.get("fecha_termino"),
            turno_actual=datos.get("turno_actual"),
            condicion_alumno=datos.get("condicion_alumno")
        )
