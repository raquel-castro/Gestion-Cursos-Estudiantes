
from datetime import date
from typing import Optional
from pydantic import BaseModel, Field, field_validator


CICLOS_VALIDOS = {"I", "II", "III", "IV", "V", "VI"}
CONDICIONES_VALIDAS = {"NUEVO", "REGULAR", "REINGRESO"}


class MatriculaCrear(BaseModel):
    id_alumno: int = Field(gt=0)
    ciclo: str
    periodo_academico: str = Field(
        min_length=6,
        max_length=10,
        pattern=r"^\d{4}-(I|II)$"
    )
    condicion: str

    @field_validator("ciclo", "condicion")
    @classmethod
    def validar_opciones(cls, valor, info):
        valor = valor.strip().upper()

        if info.field_name == "ciclo" and valor not in CICLOS_VALIDOS:
            raise ValueError("El ciclo debe ser I, II, III, IV, V o VI")

        if info.field_name == "condicion" and valor not in CONDICIONES_VALIDAS:
            raise ValueError("La condición debe ser NUEVO, REGULAR o REINGRESO")

        return valor


class MatriculaActualizar(BaseModel):
    ciclo: Optional[str] = None
    periodo_academico: Optional[str] = Field(
        default=None,
        min_length=6,
        max_length=10,
        pattern=r"^\d{4}-(I|II)$"
    )
    condicion: Optional[str] = None

    @field_validator("ciclo", "condicion")
    @classmethod
    def validar_opciones(cls, valor, info):
        if valor is None:
            return valor

        valor = valor.strip().upper()

        if info.field_name == "ciclo" and valor not in CICLOS_VALIDOS:
            raise ValueError("Ciclo inválido")

        if info.field_name == "condicion" and valor not in CONDICIONES_VALIDAS:
            raise ValueError("Condición inválida")

        return valor


class MatriculaRespuesta(BaseModel):
    id_matricula: int
    fecha_matricula: date
    estado: str
    id_alumno: int
    id_curso: Optional[int] = None
    carrera: Optional[str] = None
    turno: Optional[str] = None
    ciclo: Optional[str] = None
    periodo_academico: Optional[str] = None
    condicion: Optional[str] = None
