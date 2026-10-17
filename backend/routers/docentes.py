
from fastapi import APIRouter, HTTPException, Path, Query
from pydantic import BaseModel, Field
class DocenteCrearConCursos(BaseModel):
    especialidad: str
    id_persona: int
    ids_cursos: list[int] = Field(default_factory=list)
import psycopg2

from Dao.docente_dao import (
    DocenteDAO,
    DocenteNoEncontradoError,
    DocenteConCursosError
)

from models.docente import Docente
from schemas.docente_schema import (
    DocenteCrear,
    DocenteActualizar,
    DocenteRespuesta
)


router = APIRouter(
    prefix="/docentes",
    tags=["Docentes"]
)

dao = DocenteDAO()

ID = Path(gt=0, le=2147483647)


# ==========================================
# ESQUEMA PARA ASIGNAR CURSOS
# ==========================================

class AsignacionCursos(BaseModel):
    ids_cursos: list[int] = Field(default_factory=list)


# ==========================================
# LISTAR DOCENTES
# ==========================================

@router.get("/", response_model=list[DocenteRespuesta])
def listar_docentes():
    return [
        d.to_dict()
        for d in dao.obtener_todos()
    ]


# ==========================================
# BUSCAR DOCENTES
# ==========================================

@router.get("/buscar", response_model=list[DocenteRespuesta])
def buscar_docentes(
    id: int | None = Query(
        default=None,
        gt=0,
        le=2147483647
    ),
    especialidad: str | None = Query(
        default=None,
        min_length=1
    ),
    nombre: str | None = Query(
        default=None,
        min_length=1
    )
):
    if id is not None:
        d = dao.buscar_por_id(id)
        return [d.to_dict()] if d else []

    if not any([especialidad, nombre]):
        raise HTTPException(
            status_code=400,
            detail=(
                "Debe indicar especialidad o nombre "
                "para realizar la búsqueda."
            )
        )

    return [
        d.to_dict()
        for d in dao.buscar(especialidad, nombre)
    ]


# ==========================================
# OBTENER DOCENTE POR ID
# ==========================================

@router.get("/{docente_id}", response_model=DocenteRespuesta)
def obtener_docente(docente_id: int = ID):
    d = dao.buscar_por_id(docente_id)

    if not d:
        raise HTTPException(
            status_code=404,
            detail=f"Docente ID={docente_id} no encontrado"
        )

    return d.to_dict()


# ==========================================
# REGISTRAR DOCENTE
# ==========================================

@router.post(
    "/",
    response_model=DocenteRespuesta,
    status_code=201
)
def crear_docente(datos: DocenteCrear):
    try:
        d = dao.insertar(
            Docente(
                0,
                datos.especialidad,
                datos.id_persona
            )
        )

        return d.to_dict()

    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(
            status_code=400,
            detail="La persona indicada no existe."
        )

    except psycopg2.Error:
        raise HTTPException(
            status_code=500,
            detail="No se pudo registrar el docente."
        )


# ==========================================
# ACTUALIZAR DOCENTE
# ==========================================

@router.put(
    "/{docente_id}",
    response_model=DocenteRespuesta
)
def actualizar_docente(
    datos: DocenteActualizar,
    docente_id: int = ID
):
    try:
        d = dao.actualizar(
            docente_id,
            datos.especialidad,
            datos.id_persona
        )

        return d.to_dict()

    except DocenteNoEncontradoError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex)
        )

    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(
            status_code=400,
            detail="La persona indicada no existe."
        )

    except psycopg2.Error:
        raise HTTPException(
            status_code=500,
            detail="No se pudo actualizar el docente."
        )


# ==========================================
# ELIMINAR DOCENTE
# ==========================================

@router.delete("/{docente_id}")
def eliminar_docente(docente_id: int = ID):
    try:
        dao.eliminar(docente_id)

        return {
            "mensaje": (
                f"Docente ID={docente_id} eliminado"
            )
        }

    except DocenteNoEncontradoError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex)
        )

    except DocenteConCursosError as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex)
        )

    except psycopg2.Error:
        raise HTTPException(
            status_code=500,
            detail="No se pudo eliminar el docente."
        )


# ==========================================
# ASIGNAR CURSOS AL DOCENTE
# ==========================================

@router.put("/{docente_id}/cursos")
def asignar_cursos_docente(
    datos: AsignacionCursos,
    docente_id: int = ID
):
    try:
        if any(
            id_curso <= 0
            for id_curso in datos.ids_cursos
        ):
            raise HTTPException(
                status_code=400,
                detail="Los ID de cursos deben ser positivos."
            )

        dao.asignar_cursos(
            docente_id,
            datos.ids_cursos
        )

        return {
            "mensaje": "Cursos asignados correctamente",
            "id_docente": docente_id,
            "ids_cursos": datos.ids_cursos
        }

    except DocenteNoEncontradoError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex)
        )

    except ValueError as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex)
        )

    except psycopg2.Error:
        raise HTTPException(
            status_code=500,
            detail="No se pudieron asignar los cursos."
        )


# ==========================================
# CONSULTAR CURSOS DE UN DOCENTE
# ==========================================

@router.get("/{docente_id}/cursos")
def consultar_cursos_docente(
    docente_id: int = ID
):
    docente = dao.buscar_por_id(docente_id)

    if not docente:
        raise HTTPException(
            status_code=404,
            detail="El docente no existe."
        )

    return dao.obtener_cursos_docente(docente_id)

# ==========================================
# REGISTRAR DOCENTE CON SUS CURSOS
# ==========================================

@router.post(
    "/con-cursos",
    response_model=DocenteRespuesta,
    status_code=201
)
def crear_docente_con_cursos(
    datos: DocenteCrearConCursos
):
    try:
        if not datos.especialidad.strip():
            raise HTTPException(
                status_code=400,
                detail="Debe seleccionar una carrera."
            )

        if any(id_curso <= 0 for id_curso in datos.ids_cursos):
            raise HTTPException(
                status_code=400,
                detail="Los ID de cursos deben ser positivos."
            )

        docente = Docente(
            0,
            datos.especialidad.strip(),
            datos.id_persona
        )

        registrado = dao.insertar_con_cursos(
            docente,
            datos.ids_cursos
        )

        return registrado.to_dict()

    except ValueError as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex)
        )

    except psycopg2.errors.UniqueViolation:
        raise HTTPException(
            status_code=409,
            detail="Esta persona ya está registrada como docente."
        )

    except psycopg2.Error:
        raise HTTPException(
            status_code=500,
            detail="No se pudo registrar el docente con sus cursos."
        )
