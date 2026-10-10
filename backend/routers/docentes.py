from fastapi import APIRouter, HTTPException, Path, Query
import psycopg2
from Dao.docente_dao import DocenteDAO, DocenteNoEncontradoError, DocenteConCursosError
from models.docente import Docente
from schemas.docente_schema import DocenteCrear, DocenteActualizar, DocenteRespuesta

router = APIRouter(prefix="/docentes", tags=["Docentes"])
dao = DocenteDAO()
ID = Path(gt=0, le=2147483647)

@router.get("/", response_model=list[DocenteRespuesta])
def listar_docentes():
    return [d.to_dict() for d in dao.obtener_todos()]

@router.get("/buscar", response_model=list[DocenteRespuesta])
def buscar_docentes(
    id: int | None = Query(default=None, gt=0, le=2147483647),
    especialidad: str | None = Query(default=None, min_length=1),
    nombre: str | None = Query(default=None, min_length=1)
):
    if id is not None:
        d = dao.buscar_por_id(id)
        return [d.to_dict()] if d else []
    if not any([especialidad, nombre]):
        raise HTTPException(status_code=400, detail="Debe indicar especialidad o nombre para realizar la búsqueda.")
    return [d.to_dict() for d in dao.buscar(especialidad, nombre)]

@router.get("/{docente_id}", response_model=DocenteRespuesta)
def obtener_docente(docente_id: int = ID):
    d = dao.buscar_por_id(docente_id)
    if not d:
        raise HTTPException(status_code=404, detail=f"Docente ID={docente_id} no encontrado")
    return d.to_dict()

@router.post("/", response_model=DocenteRespuesta, status_code=201)
def crear_docente(datos: DocenteCrear):
    try:
        d = dao.insertar(Docente(0, datos.especialidad, datos.id_persona))
        return d.to_dict()
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="La persona indicada no existe.")
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo registrar el docente.")

@router.put("/{docente_id}", response_model=DocenteRespuesta)
def actualizar_docente(datos: DocenteActualizar, docente_id: int = ID):
    try:
        d = dao.actualizar(docente_id, datos.especialidad, datos.id_persona)
        return d.to_dict()
    except DocenteNoEncontradoError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except psycopg2.errors.ForeignKeyViolation:
        raise HTTPException(status_code=400, detail="La persona indicada no existe.")
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el docente.")

@router.delete("/{docente_id}")
def eliminar_docente(docente_id: int = ID):
    try:
        dao.eliminar(docente_id)
        return {"mensaje": f"Docente ID={docente_id} eliminado"}
    except DocenteNoEncontradoError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except DocenteConCursosError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo eliminar el docente.")
