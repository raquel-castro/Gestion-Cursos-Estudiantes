from fastapi import APIRouter, HTTPException, Path, Query
import psycopg2
from Dao.matricula_dao import MatriculaDAO, MatriculaNoEncontradaError, MatriculaDuplicadaError
from models.matricula import Matricula
from schemas.matricula_schema import MatriculaCrear, MatriculaActualizar, MatriculaRespuesta

router = APIRouter(prefix="/matriculas", tags=["Matrículas"])
dao = MatriculaDAO()
ID = Path(gt=0, le=2147483647)

@router.get("/", response_model=list[MatriculaRespuesta])
def listar_matriculas():
    return [m.to_dict() for m in dao.obtener_todos()]

@router.get("/buscar", response_model=list[MatriculaRespuesta])
def buscar_matriculas(
    id: int | None = Query(default=None, gt=0, le=2147483647),
    id_alumno: int | None = Query(default=None, gt=0, le=2147483647),
    id_curso: int | None = Query(default=None, gt=0, le=2147483647),
    estado: str | None = Query(default=None, min_length=1)
):
    if id is not None:
        m = dao.buscar_por_id(id)
        return [m.to_dict()] if m else []
    if not any([id_alumno is not None, id_curso is not None, estado]):
        raise HTTPException(status_code=400, detail="Debe indicar alumno, curso o estado para realizar la búsqueda.")
    if estado and estado.strip().upper() not in {"ACTIVO", "RETIRADO", "FINALIZADO"}:
        raise HTTPException(status_code=400, detail="El estado debe ser ACTIVO, RETIRADO o FINALIZADO.")
    return [m.to_dict() for m in dao.buscar(id_alumno, id_curso, estado)]

@router.get("/alumno/{alumno_id}", response_model=list[MatriculaRespuesta])
def matriculas_por_alumno(alumno_id: int = ID):
    return [m.to_dict() for m in dao.buscar(id_alumno=alumno_id)]

@router.get("/curso/{curso_id}", response_model=list[MatriculaRespuesta])
def matriculas_por_curso(curso_id: int = ID):
    return [m.to_dict() for m in dao.buscar(id_curso=curso_id)]

@router.get("/{matricula_id}", response_model=MatriculaRespuesta)
def obtener_matricula(matricula_id: int = ID):
    m = dao.buscar_por_id(matricula_id)
    if not m:
        raise HTTPException(status_code=404, detail=f"Matrícula ID={matricula_id} no encontrada")
    return m.to_dict()

@router.post("/", response_model=MatriculaRespuesta, status_code=201)
def crear_matricula(datos: MatriculaCrear):
    try:
        m = dao.insertar(Matricula(0, datos.fecha_matricula, datos.estado, datos.id_alumno, datos.id_curso))
        return m.to_dict()
    except MatriculaDuplicadaError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="El alumno o el curso indicado no existe.")
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo registrar la matrícula.")

@router.put("/{matricula_id}", response_model=MatriculaRespuesta)
def actualizar_matricula(datos: MatriculaActualizar, matricula_id: int = ID):
    try:
        m = dao.actualizar(matricula_id, datos.fecha_matricula, datos.estado, datos.id_alumno, datos.id_curso)
        return m.to_dict()
    except MatriculaNoEncontradaError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except MatriculaDuplicadaError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="El alumno o el curso indicado no existe.")
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo actualizar la matrícula.")

@router.delete("/{matricula_id}")
def eliminar_matricula(matricula_id: int = ID):
    try:
        dao.eliminar(matricula_id)
        return {"mensaje": f"Matrícula ID={matricula_id} eliminada"}
    except MatriculaNoEncontradaError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo eliminar la matrícula.")
