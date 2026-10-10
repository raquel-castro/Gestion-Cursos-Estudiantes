from pydantic import BaseModel, field_validator
from typing import Optional

class CursoCrear(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    creditos: int
    ciclo: str
    horas_semanales: int
    id_docente: int

    @field_validator("creditos")
    @classmethod
    def validar_creditos(cls, valor):
        if valor <= 0:
            raise ValueError(
                "Los créditos deben ser mayores que 0"
            )
        return valor

    @field_validator("horas_semanales")
    @classmethod
    def validar_horas(cls, valor):
        if valor <= 0:
            raise ValueError(
                "Las horas semanales deben ser mayores que 0"
            )
        return valor

class CursoActualizar(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None
    creditos: Optional[int] = None
    ciclo: Optional[str] = None
    horas_semanales: Optional[int] = None
    id_docente: Optional[int] = None

    @field_validator("creditos")
    @classmethod
    def validar_creditos(cls, valor):
        if valor is not None and valor <= 0:
            raise ValueError(
                "Los créditos deben ser mayores que 0"
            )
        return valor

    @field_validator("horas_semanales")
    @classmethod
    def validar_horas(cls, valor):
        if valor is not None and valor <= 0:
            raise ValueError(
                "Las horas semanales deben ser mayores que 0"
            )
        return valor

class CursoRespuesta(BaseModel):
    id_curso: int
    nombre: str
    descripcion: Optional[str] = None
    creditos: int
    ciclo: str
    horas_semanales: int
    id_docente: int
