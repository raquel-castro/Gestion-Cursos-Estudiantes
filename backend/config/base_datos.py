
import os
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv


# ==========================================
# CARGAR VARIABLES DE ENTORNO
# ==========================================

RUTA_ENV = Path(__file__).resolve().parent.parent / ".env"

load_dotenv(dotenv_path=RUTA_ENV)


# ==========================================
# CONFIGURACIÓN POSTGRESQL
# ==========================================

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PORT = os.getenv("DB_PORT", "5432")

DB_NAME = os.getenv(
    "DB_NAME",
    "db_gestion_cursos_estudiantes"
)

DB_USER = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD")


# ==========================================
# OBTENER CONEXIÓN
# ==========================================

def obtener_conexion():
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        cursor_factory=RealDictCursor
    )
