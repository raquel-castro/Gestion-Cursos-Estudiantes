import re
from typing import Optional
from pydantic import BaseModel, field_validator

EMAIL_RE = re.compile(r"^[^\s@]+@[^\s@]+\.[^\s@]+$")

class PersonaCrear(BaseModel):
    dni: str
    nombres: str
    apellidos: str
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None

    @field_validator("dni")
    @classmethod
    def validar_dni(cls, valor):
        valor = valor.strip()
        if not re.fullmatch(r"\d{8}", valor):
            raise ValueError("El DNI debe tener exactamente 8 dígitos numéricos")
        return valor

    @field_validator("nombres", "apellidos")
    @classmethod
    def validar_texto_obligatorio(cls, valor):
        valor = valor.strip()
        if not valor:
            raise ValueError("El campo no puede estar vacío")
        return valor

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor):
        if valor is None or not valor.strip():
            return None
        valor = valor.strip().lower()
        if not EMAIL_RE.fullmatch(valor):
            raise ValueError("El correo electrónico no tiene un formato válido")
        return valor

class PersonaActualizar(BaseModel):
    dni: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None

    @field_validator("dni")
    @classmethod
    def validar_dni(cls, valor):
        if valor is not None:
            valor = valor.strip()
            if not re.fullmatch(r"\d{8}", valor):
                raise ValueError("El DNI debe tener exactamente 8 dígitos numéricos")
        return valor

    @field_validator("nombres", "apellidos")
    @classmethod
    def validar_texto(cls, valor):
        if valor is not None:
            valor = valor.strip()
            if not valor:
                raise ValueError("El campo no puede estar vacío")
        return valor

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor):
        if valor is None or not valor.strip():
            return None
        valor = valor.strip().lower()
        if not EMAIL_RE.fullmatch(valor):
            raise ValueError("El correo electrónico no tiene un formato válido")
        return valor

class PersonaRespuesta(BaseModel):
    id_persona: int
    dni: str
    nombres: str
    apellidos: str
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
