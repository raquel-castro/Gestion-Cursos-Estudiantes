from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from passlib.context import CryptContext
from config.base_datos import obtener_conexion

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


class LoginRequest(BaseModel):
    nombre_usuario: str
    contrasena: str


@router.post("/login")
def login(datos: LoginRequest):
    conn = obtener_conexion()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT id_usuario, nombre_usuario, password_hash
                FROM usuario
                WHERE nombre_usuario = %s
                """,
                (datos.nombre_usuario,)
            )

            usuario = cursor.fetchone()

        if not usuario:
            raise HTTPException(
                status_code=401,
                detail="Usuario o contraseña incorrectos."
            )

        password_valida = pwd_context.verify(
            datos.contrasena,
            usuario["password_hash"]
        )

        if not password_valida:
            raise HTTPException(
                status_code=401,
                detail="Usuario o contraseña incorrectos."
            )

        return {
            "mensaje": "Inicio de sesión correcto",
            "id_usuario": usuario["id_usuario"],
            "nombre_usuario": usuario["nombre_usuario"]
        }

    finally:
        conn.close()