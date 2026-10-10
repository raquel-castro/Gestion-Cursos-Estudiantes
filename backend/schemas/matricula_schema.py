from datetime import date
from pydantic import BaseModel, field_validator
from typing import Optional

class MatriculaCrear(BaseModel):
    fecha_matricula: date
    estado: str
    id_alumno: int
    id_curso: int

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, valor):

        valor = valor.strip().upper()

        estados_validos = [
            "ACTIVO",
            "RETIRADO",
            "FINALIZADO"
        ]

        if valor not in estados_validos:
            raise ValueError(
                "El estado debe ser ACTIVO, RETIRADO o FINALIZADO"
            )
        return valor

class MatriculaActualizar(BaseModel):
    fecha_matricula: Optional[date] = None
    estado: Optional[str] = None
    id_alumno: Optional[int] = None
    id_curso: Optional[int] = None

    @field_validator("estado")
    @classmethod
    def validar_estado(cls, valor):

        if valor is None:
            return valor

        valor = valor.strip().upper()
        estados_validos = [
            "ACTIVO",
            "RETIRADO",
            "FINALIZADO"
        ]
        if valor not in estados_validos:
            raise ValueError(
                "El estado debe ser ACTIVO, RETIRADO o FINALIZADO"
            )
        return valor

class MatriculaRespuesta(BaseModel):
    id_matricula: int
    fecha_matricula: date
    estado: str
    id_alumno: int
    id_curso: int
