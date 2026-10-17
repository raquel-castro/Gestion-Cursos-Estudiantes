
from fastapi import APIRouter, HTTPException, Path, Query
import psycopg2

from Dao.cursos_dao import (
    CursoDAO,
    CursoNoEncontradoError,
    CursoDuplicadoError,
    CursoConMatriculasError
)
from models.curso import Curso
from schemas.curso_schema import (
    CursoCrear,
    CursoActualizar,
    CursoRespuesta
)

router = APIRouter(prefix="/cursos", tags=["Cursos"])
dao = CursoDAO()
ID = Path(gt=0, le=2147483647)


@router.get("/", response_model=list[CursoRespuesta])
def listar_cursos():
    return [c.to_dict() for c in dao.obtener_todos()]


@router.get("/buscar", response_model=list[CursoRespuesta])
def buscar_cursos(
    id: int | None = Query(default=None, gt=0, le=2147483647),
    nombre: str | None = Query(default=None, min_length=1),
    ciclo: str | None = Query(default=None, min_length=1),
    id_docente: int | None = Query(default=None, gt=0, le=2147483647),
    carrera: str | None = Query(default=None, min_length=1)
):
    if id is not None:
        c = dao.buscar_por_id(id)

        if c and carrera and c.carrera != carrera:
            return []

        return [c.to_dict()] if c else []

    if not any([
        nombre,
        ciclo,
        id_docente is not None,
        carrera
    ]):
        raise HTTPException(
            status_code=400,
            detail="Debe indicar al menos un criterio de búsqueda."
        )

    return [
        c.to_dict()
        for c in dao.buscar(
            nombre=nombre,
            ciclo=ciclo,
            id_docente=id_docente,
            carrera=carrera
        )
    ]


@router.get("/{curso_id}", response_model=CursoRespuesta)
def obtener_curso(curso_id: int = ID):
    c = dao.buscar_por_id(curso_id)

    if not c:
        raise HTTPException(
            status_code=404,
            detail=f"Curso ID={curso_id} no encontrado"
        )

    return c.to_dict()


@router.post("/", response_model=CursoRespuesta, status_code=201)
def crear_curso(datos: CursoCrear):
    try:
        curso = Curso(
            id_curso=0,
            nombre=datos.nombre,
            descripcion=datos.descripcion,
            creditos=datos.creditos,
            ciclo=datos.ciclo,
            horas_semanales=datos.horas_semanales,
            id_docente=datos.id_docente,
            carrera=datos.carrera
        )

        c = dao.insertar(curso)
        return c.to_dict()

    except CursoDuplicadoError as ex:
        raise HTTPException(status_code=400, detail=str(ex))

    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(
            status_code=400,
            detail="El docente indicado no existe."
        )

    except psycopg2.Error:
        raise HTTPException(
            status_code=500,
            detail="No se pudo registrar el curso."
        )


@router.put("/{curso_id}", response_model=CursoRespuesta)
def actualizar_curso(
    datos: CursoActualizar,
    curso_id: int = ID
):
    try:
        c = dao.actualizar(
            curso_id=curso_id,
            nombre=datos.nombre,
            descripcion=datos.descripcion,
            creditos=datos.creditos,
            ciclo=datos.ciclo,
            horas_semanales=datos.horas_semanales,
            id_docente=datos.id_docente,
            carrera=datos.carrera
        )

        return c.to_dict()

    except CursoNoEncontradoError as ex:
        raise HTTPException(status_code=404, detail=str(ex))

    except CursoDuplicadoError as ex:
        raise HTTPException(status_code=400, detail=str(ex))

    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(
            status_code=400,
            detail="El docente indicado no existe."
        )

    except psycopg2.Error:
        raise HTTPException(
            status_code=500,
            detail="No se pudo actualizar el curso."
        )


@router.delete("/{curso_id}")
def eliminar_curso(curso_id: int = ID):
    try:
        dao.eliminar(curso_id)

        return {
            "mensaje": f"Curso ID={curso_id} eliminado"
        }

    except CursoNoEncontradoError as ex:
        raise HTTPException(status_code=404, detail=str(ex))

    except CursoConMatriculasError as ex:
        raise HTTPException(status_code=400, detail=str(ex))

    except psycopg2.Error:
        raise HTTPException(
            status_code=500,
            detail="No se pudo eliminar el curso."
        )
