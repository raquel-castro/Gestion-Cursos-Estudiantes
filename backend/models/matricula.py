
class Matricula:

    def __init__(
        self,
        id_matricula=0,
        fecha_matricula=None,
        estado="ACTIVO",
        id_alumno=0,
        id_curso=None,
        carrera=None,
        turno=None,
        ciclo=None,
        periodo_academico=None,
        condicion=None
    ):
        self.id_matricula = id_matricula
        self.fecha_matricula = fecha_matricula
        self.estado = estado
        self.id_alumno = id_alumno
        self.id_curso = id_curso
        self.carrera = carrera
        self.turno = turno
        self.ciclo = ciclo
        self.periodo_academico = periodo_academico
        self.condicion = condicion

    def __str__(self):
        return (
            f"Matrícula {self.id_matricula} - "
            f"Alumno {self.id_alumno} - "
            f"Periodo {self.periodo_academico}"
        )

    def to_dict(self):
        return {
            "id_matricula": self.id_matricula,
            "fecha_matricula": self.fecha_matricula,
            "estado": self.estado,
            "id_alumno": self.id_alumno,
            "id_curso": self.id_curso,
            "carrera": self.carrera,
            "turno": self.turno,
            "ciclo": self.ciclo,
            "periodo_academico": self.periodo_academico,
            "condicion": self.condicion
        }

    @classmethod
    def from_dict(cls, datos):
        return cls(
            id_matricula=datos.get("id_matricula", 0),
            fecha_matricula=datos.get("fecha_matricula"),
            estado=datos.get("estado", "ACTIVO"),
            id_alumno=datos.get("id_alumno", 0),
            id_curso=datos.get("id_curso"),
            carrera=datos.get("carrera"),
            turno=datos.get("turno"),
            ciclo=datos.get("ciclo"),
            periodo_academico=datos.get("periodo_academico"),
            condicion=datos.get("condicion")
        )
