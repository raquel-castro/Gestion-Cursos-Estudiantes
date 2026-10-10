from fastapi import APIRouter, Query
from config.logger import Logger

router = APIRouter(
    prefix="/logs",
    tags=["Historial"]
)
# =========================================================
# OBTENER HISTORIAL
# =========================================================
@router.get("/")
def obtener_logs(
    buscar: str | None = Query(default=None, min_length=1)
):
    logs = Logger().obtener_logs()
    if not buscar:
        return logs
    termino = buscar.strip().lower()
    return [log for log in logs if termino in str(log.get("hora", "")).lower() or termino in str(log.get("nivel", "")).lower() or termino in str(log.get("msg", "")).lower()]
# =========================================================
# LIMPIAR HISTORIAL
# =========================================================
@router.delete("/")
def limpiar_logs():
    Logger().limpiar()
    return {
        "mensaje": "Historial de logs limpiado correctamente."
    }
