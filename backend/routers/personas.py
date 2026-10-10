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
from schemas.persona_schema import PersonaCrear, PersonaActualizar, PersonaRespuesta

router = APIRouter(prefix="/personas", tags=["Personas"])
dao = PersonaDAO()
ID = Path(gt=0, le=2147483647)

@router.get("/", response_model=list[PersonaRespuesta])
def listar_personas():
    return [p.to_dict() for p in dao.obtener_todos()]

@router.get("/buscar", response_model=list[PersonaRespuesta])
def buscar_personas(
    id: int | None = Query(default=None, gt=0, le=2147483647),
    dni: str | None = Query(default=None, min_length=1),
    nombre: str | None = Query(default=None, min_length=1),
    apellido: str | None = Query(default=None, min_length=1),
    correo: str | None = Query(default=None, min_length=3)
):
    if id is not None:
        p = dao.buscar_por_id(id)
        return [p.to_dict()] if p else []
    if not any([dni, nombre, apellido, correo]):
        raise HTTPException(status_code=400, detail="Debe indicar DNI, nombre, apellido o correo para realizar la búsqueda.")
    if dni and (not dni.isdigit() or len(dni) != 8):
        raise HTTPException(status_code=400, detail="El DNI debe tener exactamente 8 dígitos numéricos.")
    return [p.to_dict() for p in dao.buscar(dni, nombre, apellido, correo)]

@router.get("/{persona_id}", response_model=PersonaRespuesta)
def obtener_persona(persona_id: int = ID):
    p = dao.buscar_por_id(persona_id)
    if not p:
        raise HTTPException(status_code=404, detail=f"Persona ID={persona_id} no encontrada")
    return p.to_dict()

@router.post("/", response_model=PersonaRespuesta, status_code=201)
def crear_persona(datos: PersonaCrear):
    try:
        p = dao.insertar(Persona(0, datos.dni, datos.nombres, datos.apellidos, datos.telefono, datos.correo, datos.direccion))
        return p.to_dict()
    except (DNIDuplicadoError, CorreoDuplicadoError) as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo registrar la persona.")

@router.put("/{persona_id}", response_model=PersonaRespuesta)
def actualizar_persona(datos: PersonaActualizar, persona_id: int = ID):
    try:
        p = dao.actualizar(persona_id, datos.dni, datos.nombres, datos.apellidos, datos.telefono, datos.correo, datos.direccion)
        return p.to_dict()
    except PersonaNoEncontradaError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except (DNIDuplicadoError, CorreoDuplicadoError) as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo actualizar la persona.")

@router.delete("/{persona_id}")
def eliminar_persona(persona_id: int = ID):
    try:
        dao.eliminar(persona_id)
        return {"mensaje": f"Persona ID={persona_id} eliminada"}
    except PersonaNoEncontradaError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except PersonaConRegistrosError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo eliminar la persona.")
