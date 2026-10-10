from fastapi import APIRouter, HTTPException, Path, Query
import psycopg2
from Dao.alumno_dao import AlumnoDAO, AlumnoNoEncontradoError, CodigoAlumnoDuplicadoError, AlumnoConMatriculasError
from models.alumno import Alumno
from schemas.alumno_schema import AlumnoCrear, AlumnoActualizar, AlumnoRespuesta

router = APIRouter(prefix="/alumnos", tags=["Alumnos"])
dao = AlumnoDAO()
ID = Path(gt=0, le=2147483647)

@router.get("/", response_model=list[AlumnoRespuesta])
def listar_alumnos():
    return [a.to_dict() for a in dao.obtener_todos()]

@router.get("/buscar", response_model=list[AlumnoRespuesta])
def buscar_alumnos(
    id: int | None = Query(default=None, gt=0, le=2147483647),
    codigo: str | None = Query(default=None, min_length=1),
    dni: str | None = Query(default=None, min_length=1),
    nombre: str | None = Query(default=None, min_length=1),
    distrito: str | None = Query(default=None, min_length=1)
):
    if id is not None:
        a = dao.buscar_por_id(id)
        return [a.to_dict()] if a else []
    if not any([codigo, dni, nombre, distrito]):
        raise HTTPException(status_code=400, detail="Debe indicar código, DNI, nombre o distrito para realizar la búsqueda.")
    if dni and (not dni.isdigit() or len(dni) != 8):
        raise HTTPException(status_code=400, detail="El DNI debe tener exactamente 8 dígitos numéricos.")
    return [a.to_dict() for a in dao.buscar(codigo, dni, nombre, distrito)]

@router.get("/{alumno_id}", response_model=AlumnoRespuesta)
def obtener_alumno(alumno_id: int = ID):
    a = dao.buscar_por_id(alumno_id)
    if not a:
        raise HTTPException(status_code=404, detail=f"Alumno ID={alumno_id} no encontrado")
    return a.to_dict()

@router.post("/", response_model=AlumnoRespuesta, status_code=201)
def crear_alumno(datos: AlumnoCrear):
    try:
        a = dao.insertar(Alumno(0, datos.codigo_alumno, datos.id_persona, datos.id_distrito))
        return a.to_dict()
    except CodigoAlumnoDuplicadoError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="La persona o el distrito indicado no existe.")
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo registrar el alumno.")

@router.put("/{alumno_id}", response_model=AlumnoRespuesta)
def actualizar_alumno(datos: AlumnoActualizar, alumno_id: int = ID):
    try:
        a = dao.actualizar(alumno_id, datos.codigo_alumno, datos.id_persona, datos.id_distrito)
        return a.to_dict()
    except AlumnoNoEncontradoError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except CodigoAlumnoDuplicadoError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="La persona o el distrito indicado no existe.")
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el alumno.")

@router.delete("/{alumno_id}")
def eliminar_alumno(alumno_id: int = ID):
    try:
        dao.eliminar(alumno_id)
        return {"mensaje": f"Alumno ID={alumno_id} eliminado"}
    except AlumnoNoEncontradoError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except AlumnoConMatriculasError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo eliminar el alumno.")
