
from pydantic import BaseModel, Field
from typing import Optional


# ==========================================
# REGISTRAR DOCENTE
# ==========================================

class DocenteCrear(BaseModel):
    especialidad: str
    id_persona: int


# ==========================================
# ACTUALIZAR DOCENTE
# ==========================================

class DocenteActualizar(BaseModel):
    especialidad: Optional[str] = None
    id_persona: Optional[int] = None


# ==========================================
# RESPUESTA DOCENTE
# ==========================================

class DocenteRespuesta(BaseModel):
    id_docente: int
    especialidad: str
    id_persona: int


# ==========================================
# ASIGNAR CURSOS A DOCENTE
# ==========================================

class AsignacionCursos(BaseModel):
    ids_cursos: list[int] = Field(default_factory=list)
