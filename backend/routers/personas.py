from fastapi import APIRouter, HTTPException, Path, Query
import psycopg2

from Dao.persona_dao import (
    PersonaDAO,
    PersonaNoEncontradaError,
    DNIDuplicadoError,
    CorreoDuplicadoError,
    PersonaConRegistrosError
)

from models.persona import Persona
from schemas.persona_schema import (
    PersonaCrear,
    PersonaActualizar,
    PersonaRespuesta
)


router = APIRouter(
    prefix="/personas",
    tags=["Personas"]
)

dao = PersonaDAO()

ID = Path(
    gt=0,
    le=2147483647
)


# ==========================================
# LISTAR PERSONAS
# ==========================================

@router.get(
    "/",
    response_model=list[PersonaRespuesta]
)
def listar_personas():

    return [
        p.to_dict()
        for p in dao.obtener_todos()
    ]


# ==========================================
# BUSCAR PERSONAS
# ==========================================

@router.get(
    "/buscar",
    response_model=list[PersonaRespuesta]
)
def buscar_personas(
    dni: str | None = Query(
        default=None,
        min_length=1
    ),
    nombre: str | None = Query(
        default=None,
        min_length=1
    ),
    apellido: str | None = Query(
        default=None,
        min_length=1
    )
):

    if not any([
        dni,
        nombre,
        apellido
    ]):

        raise HTTPException(
            status_code=400,
            detail=(
                "Debe indicar DNI, nombre o apellido "
                "para realizar la búsqueda."
            )
        )

    if dni:

        if (
            not dni.isdigit()
            or len(dni) != 8
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "El DNI debe tener exactamente "
                    "8 dígitos numéricos."
                )
            )

    personas = dao.buscar(
        dni=dni,
        nombre=nombre,
        apellido=apellido
    )

    return [
        p.to_dict()
        for p in personas
    ]


# ==========================================
# OBTENER PERSONA POR ID
# ==========================================

@router.get(
    "/{persona_id}",
    response_model=PersonaRespuesta
)
def obtener_persona(
    persona_id: int = ID
):

    p = dao.buscar_por_id(
        persona_id
    )

    if not p:

        raise HTTPException(
            status_code=404,
            detail=(
                f"Persona ID={persona_id} "
                f"no encontrada"
            )
        )

    return p.to_dict()


# ==========================================
# CREAR PERSONA
# ==========================================

@router.post(
    "/",
    response_model=PersonaRespuesta,
    status_code=201
)
def crear_persona(
    datos: PersonaCrear
):

    try:

        persona = Persona(
            id_persona=0,
            dni=datos.dni,
            nombres=datos.nombres,
            apellidos=datos.apellidos,
            telefono=datos.telefono,
            correo=datos.correo,
            direccion=datos.direccion,
            fecha_nacimiento=datos.fecha_nacimiento,
            id_distrito=datos.id_distrito
        )

        p = dao.insertar(
            persona
        )

        return p.to_dict()

    except (
        DNIDuplicadoError,
        CorreoDuplicadoError
    ) as ex:

        raise HTTPException(
            status_code=400,
            detail=str(ex)
        )

    except psycopg2.ForeignKeyViolation:

        raise HTTPException(
            status_code=400,
            detail=(
                "El distrito seleccionado "
                "no existe."
            )
        )

    except psycopg2.Error:

        raise HTTPException(
            status_code=500,
            detail=(
                "No se pudo registrar "
                "la persona."
            )
        )


# ==========================================
# ACTUALIZAR PERSONA
# ==========================================

@router.put(
    "/{persona_id}",
    response_model=PersonaRespuesta
)
def actualizar_persona(
    datos: PersonaActualizar,
    persona_id: int = ID
):

    try:

        p = dao.actualizar(
            persona_id=persona_id,
            dni=datos.dni,
            nombres=datos.nombres,
            apellidos=datos.apellidos,
            fecha_nacimiento=datos.fecha_nacimiento,
            telefono=datos.telefono,
            correo=datos.correo,
            direccion=datos.direccion,
            id_distrito=datos.id_distrito
        )

        return p.to_dict()

    except PersonaNoEncontradaError as ex:

        raise HTTPException(
            status_code=404,
            detail=str(ex)
        )

    except (
        DNIDuplicadoError,
        CorreoDuplicadoError
    ) as ex:

        raise HTTPException(
            status_code=400,
            detail=str(ex)
        )

    except psycopg2.ForeignKeyViolation:

        raise HTTPException(
            status_code=400,
            detail=(
                "El distrito seleccionado "
                "no existe."
            )
        )

    except psycopg2.Error:

        raise HTTPException(
            status_code=500,
            detail=(
                "No se pudo actualizar "
                "la persona."
            )
        )


# ==========================================
# ELIMINAR PERSONA
# ==========================================

@router.delete(
    "/{persona_id}"
)
def eliminar_persona(
    persona_id: int = ID
):

    try:

        dao.eliminar(
            persona_id
        )

        return {
            "mensaje": (
                f"Persona ID={persona_id} "
                f"eliminada"
            )
        }

    except PersonaNoEncontradaError as ex:

        raise HTTPException(
            status_code=404,
            detail=str(ex)
        )

    except PersonaConRegistrosError as ex:

        raise HTTPException(
            status_code=400,
            detail=str(ex)
        )

    except psycopg2.Error:

        raise HTTPException(
            status_code=500,
            detail=(
                "No se pudo eliminar "
                "la persona."
            )
        )