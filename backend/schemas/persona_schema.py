import re
from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator


EMAIL_RE = re.compile(
    r"^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$"
)

TEXTO_RE = re.compile(
    r"^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+$"
)


class PersonaCrear(BaseModel):
    dni: str
    nombres: str
    apellidos: str
    fecha_nacimiento: date
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    id_distrito: int

    @field_validator("dni")
    @classmethod
    def validar_dni(cls, valor):
        valor = valor.strip()

        if not re.fullmatch(r"\d{8}", valor):
            raise ValueError(
                "El DNI debe tener exactamente 8 dígitos numéricos"
            )

        return valor

    @field_validator("nombres", "apellidos")
    @classmethod
    def validar_nombres_apellidos(cls, valor):
        valor = " ".join(valor.strip().split())

        if not valor:
            raise ValueError(
                "El campo no puede estar vacío"
            )

        if not TEXTO_RE.fullmatch(valor):
            raise ValueError(
                "Solo se permiten letras y espacios"
            )

        return valor

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_fecha_nacimiento(cls, valor):

        if valor > date.today():
            raise ValueError(
                "La fecha de nacimiento no puede ser futura"
            )

        return valor

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, valor):

        if valor is None or not valor.strip():
            return None

        valor = valor.strip()

        if not re.fullmatch(r"\d{9}", valor):
            raise ValueError(
                "El teléfono debe tener exactamente 9 dígitos numéricos"
            )

        return valor

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor):

        if valor is None or not valor.strip():
            return None

        valor = valor.strip().lower()

        if " " in valor:
            raise ValueError(
                "El correo no puede contener espacios"
            )

        if not EMAIL_RE.fullmatch(valor):
            raise ValueError(
                "El correo electrónico no tiene un formato válido"
            )

        return valor

    @field_validator("direccion")
    @classmethod
    def validar_direccion(cls, valor):

        if valor is None or not valor.strip():
            return None

        return valor.strip()

    @field_validator("id_distrito")
    @classmethod
    def validar_distrito(cls, valor):

        if valor <= 0:
            raise ValueError(
                "Debe seleccionar un distrito válido"
            )

        return valor


class PersonaActualizar(BaseModel):
    dni: Optional[str] = None
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    fecha_nacimiento: Optional[date] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    id_distrito: Optional[int] = None

    @field_validator("dni")
    @classmethod
    def validar_dni(cls, valor):

        if valor is None:
            return valor

        valor = valor.strip()

        if not re.fullmatch(r"\d{8}", valor):
            raise ValueError(
                "El DNI debe tener exactamente 8 dígitos numéricos"
            )

        return valor

    @field_validator("nombres", "apellidos")
    @classmethod
    def validar_nombres_apellidos(cls, valor):

        if valor is None:
            return valor

        valor = " ".join(valor.strip().split())

        if not valor:
            raise ValueError(
                "El campo no puede estar vacío"
            )

        if not TEXTO_RE.fullmatch(valor):
            raise ValueError(
                "Solo se permiten letras y espacios"
            )

        return valor

    @field_validator("fecha_nacimiento")
    @classmethod
    def validar_fecha_nacimiento(cls, valor):

        if valor is not None and valor > date.today():
            raise ValueError(
                "La fecha de nacimiento no puede ser futura"
            )

        return valor

    @field_validator("telefono")
    @classmethod
    def validar_telefono(cls, valor):

        if valor is None or not valor.strip():
            return None

        valor = valor.strip()

        if not re.fullmatch(r"\d{9}", valor):
            raise ValueError(
                "El teléfono debe tener exactamente 9 dígitos numéricos"
            )

        return valor

    @field_validator("correo")
    @classmethod
    def validar_correo(cls, valor):

        if valor is None or not valor.strip():
            return None

        valor = valor.strip().lower()

        if " " in valor:
            raise ValueError(
                "El correo no puede contener espacios"
            )

        if not EMAIL_RE.fullmatch(valor):
            raise ValueError(
                "El correo electrónico no tiene un formato válido"
            )

        return valor

    @field_validator("direccion")
    @classmethod
    def validar_direccion(cls, valor):

        if valor is None or not valor.strip():
            return None

        return valor.strip()

    @field_validator("id_distrito")
    @classmethod
    def validar_distrito(cls, valor):

        if valor is not None and valor <= 0:
            raise ValueError(
                "Debe seleccionar un distrito válido"
            )

        return valor


class PersonaRespuesta(BaseModel):
    id_persona: int
    dni: str
    nombres: str
    apellidos: str
    fecha_nacimiento: Optional[date] = None
    edad: Optional[int] = None
    telefono: Optional[str] = None
    correo: Optional[str] = None
    direccion: Optional[str] = None
    id_distrito: Optional[int] = None
    distrito: Optional[str] = None