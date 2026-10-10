from fastapi import APIRouter, HTTPException, Path, Query
import psycopg2
from Dao.distrito_dao import DistritoDAO, DistritoNoEncontradoError, DistritoDuplicadoError, DistritoConRegistrosError
from models.distrito import Distrito
from schemas.distrito_schema import DistritoCrear, DistritoActualizar, DistritoRespuesta

router = APIRouter(prefix="/distritos", tags=["Distritos"])
dao = DistritoDAO()
ID = Path(gt=0, le=2147483647)

@router.get("/", response_model=list[DistritoRespuesta])
def listar_distritos():
    return [d.to_dict() for d in dao.obtener_todos()]

@router.get("/buscar", response_model=list[DistritoRespuesta])
def buscar_distritos(
    id: int | None = Query(default=None, gt=0, le=2147483647),
    nombre: str | None = Query(default=None, min_length=1)
):
    if id is not None:
        d = dao.buscar_por_id(id)
        return [d.to_dict()] if d else []
    if not nombre:
        raise HTTPException(status_code=400, detail="Debe indicar ID o nombre para realizar la búsqueda.")
    return [d.to_dict() for d in dao.buscar(nombre)]

@router.get("/{distrito_id}", response_model=DistritoRespuesta)
def obtener_distrito(distrito_id: int = ID):
    d = dao.buscar_por_id(distrito_id)
    if not d:
        raise HTTPException(status_code=404, detail=f"Distrito ID={distrito_id} no encontrado")
    return d.to_dict()

@router.post("/", response_model=DistritoRespuesta, status_code=201)
def crear_distrito(datos: DistritoCrear):
    try:
        return dao.insertar(Distrito(0, datos.nombre)).to_dict()
    except DistritoDuplicadoError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo registrar el distrito.")

@router.put("/{distrito_id}", response_model=DistritoRespuesta)
def actualizar_distrito(datos: DistritoActualizar, distrito_id: int = ID):
    try:
        return dao.actualizar(distrito_id, datos.nombre).to_dict()
    except DistritoNoEncontradoError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except DistritoDuplicadoError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo actualizar el distrito.")

@router.delete("/{distrito_id}")
def eliminar_distrito(distrito_id: int = ID):
    try:
        dao.eliminar(distrito_id)
        return {"mensaje": f"Distrito ID={distrito_id} eliminado"}
    except DistritoNoEncontradoError as ex:
        raise HTTPException(status_code=404, detail=str(ex))
    except DistritoConRegistrosError as ex:
        raise HTTPException(status_code=400, detail=str(ex))
    except psycopg2.Error:
        raise HTTPException(status_code=500, detail="No se pudo eliminar el distrito.")
