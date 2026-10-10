from pydantic import BaseModel
from typing import Optional

class DocenteCrear(BaseModel):
    especialidad: str
    id_persona: int

class DocenteActualizar(BaseModel):
    especialidad: Optional[str] = None
    id_persona: Optional[int] = None

class DocenteRespuesta(BaseModel):
    id_docente: int
    especialidad: str
    id_persona: int
