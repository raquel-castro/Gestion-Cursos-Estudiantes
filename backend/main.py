import psycopg2
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from config.base_datos import Inicializar
from routers import distritos, personas, alumnos, docentes, cursos, matriculas, logs, auth

app = FastAPI(
    title="Sistema de Gestión de Cursos y Estudiantes",
    description="API REST para la gestión de estudiantes, docentes, cursos y matrículas.",
    version="3.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:5174",
        "http://localhost:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

Inicializar()

app.include_router(distritos.router)
app.include_router(personas.router)
app.include_router(alumnos.router)
app.include_router(docentes.router)
app.include_router(cursos.router)
app.include_router(matriculas.router)
app.include_router(logs.router)
app.include_router(auth.router)


@app.exception_handler(psycopg2.Error)
async def manejar_error_base_datos(request: Request, exc: psycopg2.Error):
    return JSONResponse(
        status_code=500,
        content={"detail": "No se pudo completar la operación con la base de datos."}
    )


@app.get("/")
def inicio():
    return {
        "mensaje": "API del Sistema de Gestión de Cursos y Estudiantes funcionando correctamente",
        "version": "3.0.0"
    }
