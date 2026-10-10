from pydantic import BaseModel
from typing import Optional

class DistritoCrear(BaseModel):
    nombre: str

class DistritoActualizar(BaseModel):
    nombre: Optional[str] = None

class DistritoRespuesta(BaseModel):
    id_distrito: int
    nombre: str
