
from fastapi import APIRouter, HTTPException, Path, Query
import psycopg2

from Dao.matricula_dao import (
    MatriculaDAO,
    MatriculaNoEncontradaError,
    MatriculaDuplicadaError,
    AlumnoNoEncontradoError,
    DatosAlumnoIncompletosError
)

from schemas.matricula_schema import (
    MatriculaCrear,
    MatriculaActualizar,
    MatriculaRespuesta
)


router = APIRouter(
    prefix="/matriculas",
    tags=["Matrículas"]
)

dao = MatriculaDAO()

ID = Path(gt=0, le=2147483647)


# LISTAR MATRÍCULAS
@router.get("/", response_model=list[MatriculaRespuesta])
def listar_matriculas():
    return [m.to_dict() for m in dao.obtener_todos()]


# BUSCAR MATRÍCULAS
@router.get("/buscar", response_model=list[MatriculaRespuesta])
def buscar_matriculas(
    id_alumno: int | None = Query(default=None, gt=0),
    carrera: str | None = None,
    turno: str | None = None,
    ciclo: str | None = None,
    periodo_academico: str | None = None,
    condicion: str | None = None
):
    resultados = dao.buscar(
        id_alumno=id_alumno,
        carrera=carrera,
        turno=turno,
        ciclo=ciclo,
        periodo_academico=periodo_academico,
        condicion=condicion
    )

    return [m.to_dict() for m in resultados]


# MATRÍCULAS DE UN ALUMNO
@router.get(
    "/alumno/{alumno_id}",
    response_model=list[MatriculaRespuesta]
)
def matriculas_por_alumno(alumno_id: int = ID):
    return [
        m.to_dict()
        for m in dao.buscar(id_alumno=alumno_id)
    ]


# OBTENER MATRÍCULA POR ID
@router.get(
    "/{matricula_id}",
    response_model=MatriculaRespuesta
)
def obtener_matricula(matricula_id: int = ID):
    matricula = dao.buscar_por_id(matricula_id)

    if not matricula:
        raise HTTPException(
            status_code=404,
            detail="Matrícula no encontrada"
        )

    return matricula.to_dict()


# REGISTRAR MATRÍCULA
@router.post(
    "/",
    response_model=MatriculaRespuesta,
    status_code=201
)
def crear_matricula(datos: MatriculaCrear):
    try:
        matricula = dao.insertar(datos)
        return matricula.to_dict()

    except AlumnoNoEncontradoError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex)
        )

    except DatosAlumnoIncompletosError as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex)
        )

    except MatriculaDuplicadaError as ex:
        raise HTTPException(
            status_code=409,
            detail=str(ex)
        )

    except psycopg2.Error:
        raise HTTPException(
            status_code=500,
            detail="No se pudo registrar la matrícula"
        )


# ACTUALIZAR MATRÍCULA
@router.put(
    "/{matricula_id}",
    response_model=MatriculaRespuesta
)
def actualizar_matricula(
    datos: MatriculaActualizar,
    matricula_id: int = ID
):
    try:
        matricula = dao.actualizar(matricula_id, datos)

        if not matricula:
            raise HTTPException(
                status_code=404,
                detail="Matrícula no encontrada"
            )

        return matricula.to_dict()

    except MatriculaNoEncontradaError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex)
        )

    except MatriculaDuplicadaError as ex:
        raise HTTPException(
            status_code=409,
            detail=str(ex)
        )

    except psycopg2.Error:
        raise HTTPException(
            status_code=500,
            detail="No se pudo actualizar la matrícula"
        )


# ELIMINAR MATRÍCULA
@router.delete("/{matricula_id}")
def eliminar_matricula(matricula_id: int = ID):
    try:
        dao.eliminar(matricula_id)

        return {
            "mensaje": "Matrícula eliminada correctamente"
        }

    except MatriculaNoEncontradaError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex)
        )

    except psycopg2.Error:
        raise HTTPException(
            status_code=500,
            detail="No se pudo eliminar la matrícula"
        )
