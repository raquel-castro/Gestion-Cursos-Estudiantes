
from datetime import date

import psycopg2
from fastapi import APIRouter, HTTPException, Path, Query

from config.base_datos import obtener_conexion
from Dao.alumno_dao import (
    AlumnoDAO,
    AlumnoNoEncontradoError,
    AlumnoConMatriculasError
)
from models.alumno import Alumno
from schemas.alumno_schema import (
    AlumnoCrear,
    AlumnoActualizar,
    AlumnoRespuesta
)


router = APIRouter(
    prefix="/alumnos",
    tags=["Alumnos"]
)

dao = AlumnoDAO()

ID = Path(gt=0, le=2147483647)


# ==========================================
# BUSCAR PERSONA POR DNI
# ==========================================

def obtener_persona_por_dni(dni):
    conn = obtener_conexion()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    id_persona,
                    dni,
                    nombres,
                    apellidos
                FROM persona
                WHERE dni = %s
                """,
                (dni,)
            )

            return cursor.fetchone()

    finally:
        conn.close()


# ==========================================
# CONSTRUIR RESPUESTA
# ==========================================

def construir_respuesta(alumno):
    conn = obtener_conexion()

    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT
                    dni,
                    nombres,
                    apellidos
                FROM persona
                WHERE id_persona = %s
                """,
                (alumno.id_persona,)
            )

            persona = cursor.fetchone()

    finally:
        conn.close()

    if persona is None:
        raise HTTPException(
            status_code=500,
            detail="El alumno no tiene una persona asociada."
        )

    datos = alumno.to_dict()

    datos["dni"] = persona["dni"]

    datos["nombre_completo"] = (
        f"{persona['nombres']} {persona['apellidos']}"
    ).strip()

    return AlumnoRespuesta(**datos)


# ==========================================
# CONSULTAR PERSONA POR DNI
# ==========================================

@router.get("/persona/{dni}")
def consultar_persona(dni: str):
    dni = dni.strip()

    if (
        len(dni) != 8
        or not all("0" <= c <= "9" for c in dni)
    ):
        raise HTTPException(
            status_code=400,
            detail="El DNI debe tener exactamente 8 dígitos."
        )

    persona = obtener_persona_por_dni(dni)

    if persona is None:
        raise HTTPException(
            status_code=404,
            detail="Persona no registrada. Regístrela primero."
        )

    return {
        "dni": persona["dni"],
        "nombres": persona["nombres"],
        "apellidos": persona["apellidos"]
    }


# ==========================================
# LISTAR ALUMNOS
# ==========================================

@router.get(
    "/",
    response_model=list[AlumnoRespuesta]
)
def listar_alumnos():
    return [
        construir_respuesta(alumno)
        for alumno in dao.obtener_todos()
    ]


# ==========================================
# BUSCAR ALUMNOS
# ==========================================

@router.get(
    "/buscar",
    response_model=list[AlumnoRespuesta]
)
def buscar_alumnos(
    dni: str | None = Query(default=None),
    nombres: str | None = Query(default=None),
    apellidos: str | None = Query(default=None),
    nombre: str | None = Query(default=None)
):
    if not any(
        valor and valor.strip()
        for valor in (dni, nombres, apellidos, nombre)
    ):
        raise HTTPException(
            status_code=400,
            detail="Ingrese DNI, nombres o apellidos."
        )

    if dni:
        dni = dni.strip()

        if (
            len(dni) != 8
            or not all("0" <= c <= "9" for c in dni)
        ):
            raise HTTPException(
                status_code=400,
                detail="El DNI debe tener exactamente 8 dígitos."
            )

    return [
        construir_respuesta(alumno)
        for alumno in dao.buscar(
            dni=dni,
            nombres=nombres,
            apellidos=apellidos,
            nombre=nombre
        )
    ]


# ==========================================
# OBTENER ALUMNO POR ID
# ==========================================

@router.get(
    "/{alumno_id}",
    response_model=AlumnoRespuesta
)
def obtener_alumno(alumno_id: int = ID):
    alumno = dao.buscar_por_id(alumno_id)

    if alumno is None:
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado."
        )

    return construir_respuesta(alumno)


# ==========================================
# REGISTRAR ALUMNO
# ==========================================

@router.post(
    "/",
    response_model=AlumnoRespuesta,
    status_code=201
)
def crear_alumno(datos: AlumnoCrear):

    # Buscar la persona previamente registrada.
    persona = obtener_persona_por_dni(datos.dni)

    if persona is None:
        raise HTTPException(
            status_code=404,
            detail="Primero registre a la persona."
        )

    # Evitar registrar dos veces al mismo alumno.
    existente = dao.buscar_por_dni(datos.dni)

    if existente:
        raise HTTPException(
            status_code=409,
            detail="Esta persona ya está registrada como alumno."
        )

    # El formulario solo exige DNI, carrera y turno.
    # Los demás datos académicos son opcionales.
    alumno = Alumno(
        id_persona=persona["id_persona"],
        estado_academico="ACTIVO",
        carrera=datos.carrera,
        ciclo_ingreso=datos.ciclo_ingreso,
        fecha_ingreso=date.today(),
        fecha_termino=None,
        turno_actual=datos.turno_actual,
        condicion_alumno=datos.condicion_alumno
    )

    try:
        registrado = dao.insertar(alumno)

        return construir_respuesta(registrado)

    except ValueError as ex:
        raise HTTPException(
            status_code=409,
            detail=str(ex)
        ) from ex

    except psycopg2.IntegrityError as ex:
        raise HTTPException(
            status_code=400,
            detail="No se pudo registrar el alumno."
        ) from ex


# ==========================================
# ACTUALIZAR ALUMNO
# ==========================================

@router.put(
    "/{alumno_id}",
    response_model=AlumnoRespuesta
)
def actualizar_alumno(
    datos: AlumnoActualizar,
    alumno_id: int = ID
):
    alumno_actual = dao.buscar_por_id(alumno_id)

    if alumno_actual is None:
        raise HTTPException(
            status_code=404,
            detail="Alumno no encontrado."
        )

    cambios = datos.model_dump(exclude_unset=True)

    if not cambios:
        raise HTTPException(
            status_code=400,
            detail="No se enviaron datos para actualizar."
        )

    if any(
        valor is None
        for valor in cambios.values()
    ):
        raise HTTPException(
            status_code=400,
            detail="No se permiten valores nulos."
        )

    # Si en el futuro se modifica la condición,
    # actualizar también el estado académico.
    if "condicion_alumno" in cambios:
        condicion = cambios["condicion_alumno"]

        cambios["estado_academico"] = (
            "EGRESADO"
            if condicion == "EGRESADO"
            else "ACTIVO"
        )

        if condicion == "EGRESADO":
            if alumno_actual.fecha_termino is None:
                cambios["fecha_termino"] = date.today()

        elif alumno_actual.fecha_ingreso is None:
            cambios["fecha_ingreso"] = date.today()

    try:
        actualizado = dao.actualizar(
            alumno_id,
            **cambios
        )

        return construir_respuesta(actualizado)

    except AlumnoNoEncontradoError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex)
        ) from ex

    except ValueError as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex)
        ) from ex

    except psycopg2.IntegrityError as ex:
        raise HTTPException(
            status_code=400,
            detail="Datos académicos no válidos."
        ) from ex


# ==========================================
# ELIMINAR ALUMNO
# ==========================================

@router.delete("/{alumno_id}")
def eliminar_alumno(alumno_id: int = ID):
    try:
        dao.eliminar(alumno_id)

        return {
            "mensaje": "Alumno eliminado correctamente."
        }

    except AlumnoNoEncontradoError as ex:
        raise HTTPException(
            status_code=404,
            detail=str(ex)
        ) from ex

    except AlumnoConMatriculasError as ex:
        raise HTTPException(
            status_code=400,
            detail=str(ex)
        ) from ex
