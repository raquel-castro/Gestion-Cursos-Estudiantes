from pydantic import BaseModel
from typing import Optional

class AlumnoCrear(BaseModel):
    codigo_alumno: str
    id_persona: int
    id_distrito: int

class AlumnoActualizar(BaseModel):
    codigo_alumno: Optional[str] = None
    id_persona: Optional[int] = None
    id_distrito: Optional[int] = None

class AlumnoRespuesta(BaseModel):
    id_alumno: int
    codigo_alumno: str
    id_persona: int
    id_distrito: int
