
from datetime import date
from typing import Optional

from pydantic import BaseModel, field_validator


# ==========================================
# OPCIONES PERMITIDAS
# ==========================================

ESTADOS_VALIDOS = {
    "POSTULANTE",
    "ACTIVO",
    "RETIRADO",
    "EGRESADO"
}

CARRERAS_VALIDAS = {
    "CONTABILIDAD",
    "ADMINISTRACION",
    "DESARROLLO DE SISTEMAS DE INFORMACION"
}

CICLOS_VALIDOS = {
    "I", "II", "III", "IV", "V", "VI"
}

TURNOS_VALIDOS = {
    "MAÑANA",
    "NOCHE"
}

CONDICIONES_VALIDAS = {
    "NUEVO",
    "REGULAR",
    "EGRESADO"
}


# ==========================================
# VALIDACIONES GENERALES
# ==========================================

def validar_opcion(valor, opciones, campo):
    if valor is None:
        return None

    if not isinstance(valor, str):
        raise ValueError(f"{campo} debe ser texto")

    valor = valor.strip().upper()

    if not valor:
        return None

    if valor not in opciones:
        raise ValueError(f"{campo} no válido")

    return valor


def validar_fechas(fecha_ingreso, fecha_termino):
    if (
        fecha_ingreso is not None
        and fecha_termino is not None
        and fecha_termino < fecha_ingreso
    ):
        raise ValueError(
            "La fecha de término no puede ser anterior "
            "a la fecha de ingreso"
        )


def validar_datos_academicos(
    estado_academico,
    ciclo_ingreso,
    fecha_ingreso,
    fecha_termino
):
    validar_fechas(fecha_ingreso, fecha_termino)

    if estado_academico == "EGRESADO":
        if fecha_termino is None:
            raise ValueError(
                "Un alumno egresado debe tener fecha de término"
            )

    if estado_academico == "ACTIVO":
        if fecha_ingreso is None:
            raise ValueError(
                "Un alumno activo debe tener fecha de ingreso"
            )

    # El ciclo de ingreso ya no es obligatorio.
    # Se conserva el parámetro por compatibilidad.


# ==========================================
# REGISTRAR ALUMNO
# ==========================================

class AlumnoCrear(BaseModel):

    dni: str
    carrera: str
    turno_actual: str

    # Campos opcionales
    ciclo_ingreso: Optional[str] = None
    condicion_alumno: Optional[str] = None

    @field_validator("dni")
    @classmethod
    def validar_dni(cls, valor):
        if not isinstance(valor, str):
            raise ValueError("El DNI debe ser texto")

        valor = valor.strip()

        if len(valor) != 8 or not all(
            "0" <= caracter <= "9"
            for caracter in valor
        ):
            raise ValueError(
                "El DNI debe tener exactamente 8 dígitos numéricos"
            )

        return valor

    @field_validator("carrera")
    @classmethod
    def validar_carrera(cls, valor):
        resultado = validar_opcion(
            valor,
            CARRERAS_VALIDAS,
            "Carrera"
        )

        if resultado is None:
            raise ValueError("La carrera es obligatoria")

        return resultado

    @field_validator("turno_actual")
    @classmethod
    def validar_turno(cls, valor):
        resultado = validar_opcion(
            valor,
            TURNOS_VALIDOS,
            "Turno"
        )

        if resultado is None:
            raise ValueError("El turno es obligatorio")

        return resultado

    @field_validator("ciclo_ingreso")
    @classmethod
    def validar_ciclo(cls, valor):
        return validar_opcion(
            valor,
            CICLOS_VALIDOS,
            "Ciclo de ingreso"
        )

    @field_validator("condicion_alumno")
    @classmethod
    def validar_condicion(cls, valor):
        return validar_opcion(
            valor,
            CONDICIONES_VALIDAS,
            "Condición"
        )


# ==========================================
# ACTUALIZAR ALUMNO
# ==========================================

class AlumnoActualizar(BaseModel):

    carrera: Optional[str] = None
    turno_actual: Optional[str] = None
    ciclo_ingreso: Optional[str] = None
    condicion_alumno: Optional[str] = None

    @field_validator("carrera")
    @classmethod
    def validar_carrera(cls, valor):
        return validar_opcion(
            valor,
            CARRERAS_VALIDAS,
            "Carrera"
        )

    @field_validator("turno_actual")
    @classmethod
    def validar_turno(cls, valor):
        return validar_opcion(
            valor,
            TURNOS_VALIDOS,
            "Turno"
        )

    @field_validator("ciclo_ingreso")
    @classmethod
    def validar_ciclo(cls, valor):
        return validar_opcion(
            valor,
            CICLOS_VALIDOS,
            "Ciclo de ingreso"
        )

    @field_validator("condicion_alumno")
    @classmethod
    def validar_condicion(cls, valor):
        return validar_opcion(
            valor,
            CONDICIONES_VALIDAS,
            "Condición"
        )


# ==========================================
# RESPUESTA ALUMNO
# ==========================================

class AlumnoRespuesta(BaseModel):

    id_alumno: int
    id_persona: int

    dni: str
    nombre_completo: str

    estado_academico: Optional[str] = None
    carrera: Optional[str] = None
    ciclo_ingreso: Optional[str] = None
    fecha_ingreso: Optional[date] = None
    fecha_termino: Optional[date] = None
    turno_actual: Optional[str] = None
    condicion_alumno: Optional[str] = None
