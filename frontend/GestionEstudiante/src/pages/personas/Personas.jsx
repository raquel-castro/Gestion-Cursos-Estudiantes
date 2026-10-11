import { useEffect, useState } from "react";
import api from "../../api/axios";
import "../../components/busqueda/busqueda.css";
import "./personas.css";

import {
    alertaExito,
    alertaError,
    alertaAdvertencia,
    confirmarAccion
} from "../../utils/alertas";


const API_URL = "/personas/";
const API_DISTRITOS = "/distritos/";


function Personas() {

    const [personas, setPersonas] = useState([]);
    const [distritos, setDistritos] = useState([]);

    const [formulario, setFormulario] = useState({
        dni: "",
        nombres: "",
        apellidos: "",
        fecha_nacimiento: "",
        telefono: "",
        correo: "",
        direccion: "",
        id_distrito: ""
    });

    const [editando, setEditando] = useState(null);
    const [cargando, setCargando] = useState(true);

    const [busqueda, setBusqueda] = useState({
        dni: "",
        nombre: "",
        apellido: ""
    });


    // ==========================================
    // CALCULAR EDAD
    // ==========================================

    const calcularEdad = (fechaNacimiento) => {

        if (!fechaNacimiento) {
            return "";
        }

        const partes = fechaNacimiento.split("-");

        if (partes.length !== 3) {
            return "";
        }

        const anio = Number(partes[0]);
        const mes = Number(partes[1]);
        const dia = Number(partes[2]);

        const hoy = new Date();

        let edad = hoy.getFullYear() - anio;

        const mesActual = hoy.getMonth() + 1;
        const diaActual = hoy.getDate();

        if (
            mesActual < mes ||
            (mesActual === mes && diaActual < dia)
        ) {
            edad--;
        }

        return edad >= 0 ? edad : "";
    };


    // ==========================================
    // CARGAR PERSONAS
    // ==========================================

    const cargarPersonas = async () => {

        try {

            setCargando(true);

            const respuesta = await api.get(API_URL);

            setPersonas(respuesta.data);

        } catch (error) {

            console.error(
                "Error al obtener personas:",
                error
            );

            alertaError(
                error.response?.data?.detail ||
                "No se pudieron obtener las personas desde la API."
            );

        } finally {

            setCargando(false);
        }
    };


    // ==========================================
    // CARGAR DISTRITOS
    // ==========================================

    const cargarDistritos = async () => {

        try {

            const respuesta = await api.get(
                API_DISTRITOS
            );

            setDistritos(
                respuesta.data
            );

        } catch (error) {

            console.error(
                "Error al obtener distritos:",
                error
            );

            alertaError(
                error.response?.data?.detail ||
                "No se pudieron cargar los distritos."
            );
        }
    };


    useEffect(() => {

        cargarPersonas();
        cargarDistritos();

    }, []);


    // ==========================================
    // BUSCAR PERSONAS
    // ==========================================

    const buscarPersonas = async (e) => {

        e.preventDefault();

        const params = Object.fromEntries(
            Object.entries(busqueda)
                .filter(
                    ([, value]) =>
                        value.trim() !== ""
                )
        );

        if (
            Object.keys(params).length === 0
        ) {

            await cargarPersonas();
            return;
        }

        if (
            busqueda.dni &&
            !/^\d{8}$/.test(busqueda.dni)
        ) {

            alertaAdvertencia(
                "El DNI debe contener exactamente 8 números."
            );

            return;
        }

        try {

            setCargando(true);

            const respuesta = await api.get(
                `${API_URL}buscar`,
                {
                    params
                }
            );

            setPersonas(
                respuesta.data
            );

        } catch (error) {

            alertaError(
                error.response?.data?.detail ||
                "No se pudieron buscar las personas."
            );

        } finally {

            setCargando(false);
        }
    };


    // ==========================================
    // LIMPIAR BÚSQUEDA
    // ==========================================

    const limpiarBusqueda = async () => {

        setBusqueda({
            dni: "",
            nombre: "",
            apellido: ""
        });

        await cargarPersonas();
    };


    // ==========================================
    // CAMBIOS DEL FORMULARIO
    // ==========================================

    const manejarCambio = (e) => {

    const { name, value } = e.target;

    // DNI: solo números, máximo 8
    if (name === "dni") {

        const soloNumeros =
            value.replace(/\D/g, "");

        setFormulario({
            ...formulario,
            dni: soloNumeros.slice(0, 8)
        });

        return;
    }

    // Nombres y apellidos:
    // solo letras, espacios, tildes y ñ
    if (
        name === "nombres" ||
        name === "apellidos"
    ) {

        const soloLetras =
            value.replace(
                /[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]/g,
                ""
            );

        setFormulario({
            ...formulario,
            [name]: soloLetras
        });

        return;
    }

    // Teléfono:
    // solo números y máximo 9
    if (name === "telefono") {

        const soloNumeros =
            value.replace(/\D/g, "");

        setFormulario({
            ...formulario,
            telefono: soloNumeros.slice(0, 9)
        });

        return;
    }

    // Correo:
    // elimina espacios
    if (name === "correo") {

        setFormulario({
            ...formulario,
            correo: value.replace(/\s/g, "")
        });

        return;
    }

    setFormulario({
        ...formulario,
        [name]: value
    });
};


    // ==========================================
    // LIMPIAR FORMULARIO
    // ==========================================

    const limpiarFormulario = () => {

        setFormulario({
            dni: "",
            nombres: "",
            apellidos: "",
            fecha_nacimiento: "",
            telefono: "",
            correo: "",
            direccion: "",
            id_distrito: ""
        });

        setEditando(null);
    };


    // ==========================================
    // GUARDAR PERSONA
    // ==========================================

    const guardarPersona = async (e) => {

        e.preventDefault();

        if (
            !formulario.dni.trim() ||
            !formulario.nombres.trim() ||
            !formulario.apellidos.trim() ||
            !formulario.fecha_nacimiento ||
            !formulario.id_distrito
        ) {

            alertaAdvertencia(
                "Complete todos los campos obligatorios."
            );

            return;
        }

        if (
            !/^\d{8}$/.test(
                formulario.dni
            )
        ) {

            alertaAdvertencia(
                "El DNI debe tener exactamente 8 dígitos numéricos."
            );

            return;
        }
const textoValido =
    /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]+$/;

if (
    !textoValido.test(formulario.nombres) ||
    !textoValido.test(formulario.apellidos)
) {

    alertaAdvertencia(
        "Nombres y apellidos solo pueden contener letras."
    );

    return;
}

if (
    formulario.telefono &&
    !/^\d{9}$/.test(formulario.telefono)
) {

    alertaAdvertencia(
        "El teléfono debe tener exactamente 9 números."
    );

    return;
}

if (formulario.correo) {

    const correoValido =
        /^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$/;

    if (
        !correoValido.test(
            formulario.correo
        )
    ) {

        alertaAdvertencia(
            "Ingrese un correo electrónico válido."
        );

        return;
    }
}
        try {

            const datos = {

                dni:
                    formulario.dni.trim(),

                nombres:
                    formulario.nombres.trim(),

                apellidos:
                    formulario.apellidos.trim(),

                fecha_nacimiento:
                    formulario.fecha_nacimiento,

                telefono:
                    formulario.telefono.trim(),

                correo:
                    formulario.correo.trim(),

                direccion:
                    formulario.direccion.trim(),

                id_distrito:
                    Number(
                        formulario.id_distrito
                    )
            };


            if (editando === null) {

                await api.post(
                    API_URL,
                    datos
                );

                alertaExito(
                    "Persona registrada correctamente."
                );

            } else {

                await api.put(
                    `${API_URL}${editando}`,
                    datos
                );

                alertaExito(
                    "Persona actualizada correctamente."
                );
            }

            limpiarFormulario();

            await cargarPersonas();

        } catch (error) {

            console.error(
                "Error al guardar persona:",
                error
            );

            alertaError(
                error.response?.data?.detail ||
                "No se pudo guardar la persona."
            );
        }
    };


    // ==========================================
    // EDITAR PERSONA
    // ==========================================

    const editarPersona = (persona) => {

        setEditando(
            persona.id_persona
        );

        setFormulario({

            dni:
                persona.dni || "",

            nombres:
                persona.nombres || "",

            apellidos:
                persona.apellidos || "",

            fecha_nacimiento:
                persona.fecha_nacimiento || "",

            telefono:
                persona.telefono || "",

            correo:
                persona.correo || "",

            direccion:
                persona.direccion || "",

            id_distrito:
                persona.id_distrito
                    ? String(persona.id_distrito)
                    : ""
        });

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    };


    // ==========================================
    // ELIMINAR PERSONA
    // ==========================================

    const eliminarPersona = async (id) => {

        const confirmado =
            await confirmarAccion(
                "Esta acción eliminará permanentemente la persona seleccionada."
            );

        if (!confirmado) {
            return;
        }

        try {

            await api.delete(
                `${API_URL}${id}`
            );

            alertaExito(
                "Persona eliminada correctamente."
            );

            await cargarPersonas();

        } catch (error) {

            console.error(
                "Error al eliminar persona:",
                error
            );

            alertaError(
                error.response?.data?.detail ||
                "No se pudo eliminar la persona."
            );
        }
    };


    // ==========================================
    // FECHA MÁXIMA
    // ==========================================

    const fechaHoy =
        new Date()
            .toISOString()
            .split("T")[0];


    // ==========================================
    // VISTA
    // ==========================================

    return (

        <div className="personas-page container-fluid px-3 px-md-4 mt-4">

            {/* ENCABEZADO */}

            <div className="d-flex justify-content-between align-items-center mb-4">

                <div>

                    <h1>
                        Personas
                    </h1>

                    <p className="text-muted mb-0">
                        Gestión de personas registradas
                    </p>

                </div>

                <span className="page-count-badge">
                    {personas.length}
                </span>

            </div>


            {/* FORMULARIO */}

            <div className="card shadow-sm mb-4">

                <div className="card-body">

                    <h4 className="mb-4">

                        {
                            editando === null
                                ? "Registrar Persona"
                                : "Editar Persona"
                        }

                    </h4>


                    <form onSubmit={guardarPersona}>

                        <div className="row">


                            {/* DNI */}

                            <div className="col-md-4 mb-3">

                                <label
                                    htmlFor="dni"
                                    className="form-label"
                                >
                                    DNI *
                                </label>

                                <input
                                    id="dni"
                                    type="text"
                                    name="dni"
                                    className="form-control"
                                    placeholder="Ej: 12345678"
                                    value={formulario.dni}
                                    onChange={manejarCambio}
                                    maxLength={8}
                                    inputMode="numeric"
                                    required
                                />

                            </div>


                            {/* NOMBRES */}

                            <div className="col-md-4 mb-3">

                                <label
                                    htmlFor="nombres"
                                    className="form-label"
                                >
                                    Nombres *
                                </label>

                                <input
                                    id="nombres"
                                    type="text"
                                    name="nombres"
                                    className="form-control"
                                    placeholder="Ej: Juan Carlos"
                                    value={formulario.nombres}
                                    onChange={manejarCambio}
                                    required
                                />

                            </div>


                            {/* APELLIDOS */}

                            <div className="col-md-4 mb-3">

                                <label
                                    htmlFor="apellidos"
                                    className="form-label"
                                >
                                    Apellidos *
                                </label>

                                <input
                                    id="apellidos"
                                    type="text"
                                    name="apellidos"
                                    className="form-control"
                                    placeholder="Ej: Pérez García"
                                    value={formulario.apellidos}
                                    onChange={manejarCambio}
                                    required
                                />

                            </div>


                            {/* FECHA NACIMIENTO */}

                            <div className="col-md-4 mb-3">

                                <label
                                    htmlFor="fecha_nacimiento"
                                    className="form-label"
                                >
                                    Fecha de nacimiento *
                                </label>

                                <input
                                    id="fecha_nacimiento"
                                    type="date"
                                    name="fecha_nacimiento"
                                    className="form-control"
                                    value={
                                        formulario.fecha_nacimiento
                                    }
                                    onChange={manejarCambio}
                                    max={fechaHoy}
                                    required
                                />

                            </div>


                            {/* EDAD */}

                            <div className="col-md-2 mb-3">

                                <label
                                    htmlFor="edad"
                                    className="form-label"
                                >
                                    Edad
                                </label>

                                <input
                                    id="edad"
                                    type="text"
                                    className="form-control bg-light"
                                    value={
                                        formulario.fecha_nacimiento
                                            ? `${calcularEdad(
                                                formulario.fecha_nacimiento
                                            )} años`
                                            : ""
                                    }
                                    placeholder="Automática"
                                    readOnly
                                />

                            </div>


                            {/* DISTRITO */}

                            <div className="col-md-6 mb-3">

                                <label
                                    htmlFor="id_distrito"
                                    className="form-label"
                                >
                                    Distrito *
                                </label>

                                <select
                                    id="id_distrito"
                                    name="id_distrito"
                                    className="form-select"
                                    value={
                                        formulario.id_distrito
                                    }
                                    onChange={manejarCambio}
                                    required
                                >

                                    <option value="">
                                        Seleccione un distrito
                                    </option>

                                    {
                                        distritos.map(
                                            (distrito) => (

                                                <option
                                                    key={
                                                        distrito.id_distrito
                                                    }
                                                    value={
                                                        distrito.id_distrito
                                                    }
                                                >
                                                    {distrito.nombre}
                                                </option>

                                            )
                                        )
                                    }

                                </select>

                            </div>


                            {/* TELÉFONO */}

                            <div className="col-md-4 mb-3">

                                <label
                                    htmlFor="telefono"
                                    className="form-label"
                                >
                                    Teléfono
                                </label>

                                <input
                                    id="telefono"
                                    type="text"
                                    name="telefono"
                                    maxLength={9}
                                    inputMode="numeric"
                                    className="form-control"
                                    placeholder="Ej: 987654321"
                                    value={
                                        formulario.telefono
                                    }
                                    onChange={
                                        manejarCambio
                                    }
                                />

                            </div>


                            {/* CORREO */}

                            <div className="col-md-4 mb-3">

                                <label
                                    htmlFor="correo"
                                    className="form-label"
                                >
                                    Correo
                                </label>

                                <input
                                    id="correo"
                                    type="email"
                                    name="correo"
                                    className="form-control"
                                    placeholder="Ej: persona@gmail.com"
                                    value={
                                        formulario.correo
                                    }
                                    onChange={
                                        manejarCambio
                                    }
                                />

                            </div>


                            {/* DIRECCIÓN */}

                            <div className="col-md-4 mb-3">

                                <label
                                    htmlFor="direccion"
                                    className="form-label"
                                >
                                    Dirección
                                </label>

                                <input
                                    id="direccion"
                                    type="text"
                                    name="direccion"
                                    className="form-control"
                                    placeholder="Ej: Av. Lima 123"
                                    value={
                                        formulario.direccion
                                    }
                                    onChange={
                                        manejarCambio
                                    }
                                />

                            </div>

                        </div>


                        {/* BOTONES */}

                        <div className="d-flex gap-2">

                            <button
                                type="submit"
                                className="btn btn-primary"
                            >

                                {
                                    editando === null
                                        ? "Guardar Persona"
                                        : "Actualizar Persona"
                                }

                            </button>

                            <button
                                type="button"
                                className="btn btn-secondary"
                                onClick={
                                    limpiarFormulario
                                }
                            >
                                Limpiar
                            </button>

                        </div>

                    </form>

                </div>

            </div>


            {/* PERSONAS REGISTRADAS */}

            <div className="card shadow-sm">

                <div className="card-body">

                    <h4 className="mb-3">
                        Personas registradas
                    </h4>


                    {/* BUSCADOR */}

                    <form
                        className="row g-2 mb-4 p-3 bg-light rounded-3 border"
                        onSubmit={
                            buscarPersonas
                        }
                    >


                        {/* DNI */}

                        <div className="col-md-3">

                            <label className="form-label mb-1">
                                Buscar por DNI
                            </label>

                            <div className="personas-search-input">

                                <i
                                    className="bi bi-search"
                                    aria-hidden="true"
                                ></i>

                                <input
                                    type="text"
                                    className="form-control"
                                    placeholder="12345678"
                                    maxLength={8}
                                    inputMode="numeric"
                                    value={
                                        busqueda.dni
                                    }
                                    onChange={
                                        (e) => {

                                            const valor =
                                                e.target.value
                                                    .replace(
                                                        /\D/g,
                                                        ""
                                                    )
                                                    .slice(
                                                        0,
                                                        8
                                                    );

                                            setBusqueda({
                                                ...busqueda,
                                                dni: valor
                                            });
                                        }
                                    }
                                />

                            </div>

                        </div>


                        {/* NOMBRE */}

                        <div className="col-md-3">

                            <label className="form-label mb-1">
                                Buscar por Nombre
                            </label>

                            <div className="personas-search-input">

                                <i
                                    className="bi bi-search"
                                    aria-hidden="true"
                                ></i>

                                <input
                                    type="text"
                                    className="form-control"
                                    placeholder="Carlos"
                                    value={
                                        busqueda.nombre
                                    }
                                    onChange={
                                        (e) =>
                                            setBusqueda({
                                                ...busqueda,
                                                nombre:
                                                    e.target.value
                                            })
                                    }
                                />

                            </div>

                        </div>


                        {/* APELLIDO */}

                        <div className="col-md-3">

                            <label className="form-label mb-1">
                                Buscar por Apellido
                            </label>

                            <div className="personas-search-input">

                                <i
                                    className="bi bi-search"
                                    aria-hidden="true"
                                ></i>

                                <input
                                    type="text"
                                    className="form-control"
                                    placeholder="Ramírez"
                                    value={
                                        busqueda.apellido
                                    }
                                    onChange={
                                        (e) =>
                                            setBusqueda({
                                                ...busqueda,
                                                apellido:
                                                    e.target.value
                                            })
                                    }
                                />

                            </div>

                        </div>


                        {/* BOTONES */}

                        <div className="col-md-3 d-flex align-items-end gap-2">

                            <button
                                type="submit"
                                className="btn btn-primary flex-fill"
                            >
                                Buscar
                            </button>

                            <button
                                type="button"
                                className="btn btn-secondary"
                                onClick={
                                    limpiarBusqueda
                                }
                            >
                                Limpiar
                            </button>

                        </div>

                    </form>


                    {/* TABLA */}

                    {
                        cargando ? (

                            <div className="text-center py-4">

                                <div
                                    className="spinner-border text-primary"
                                    role="status"
                                >

                                    <span className="visually-hidden">
                                        Cargando...
                                    </span>

                                </div>

                                <p className="text-muted mt-2 mb-0">
                                    Cargando personas...
                                </p>

                            </div>

                        ) : personas.length === 0 ? (

                            <div className="alert alert-info">
                                No hay personas registradas.
                            </div>

                        ) : (

                            <div className="table-responsive">

                                <table className="table table-hover align-middle">

                                    <thead>

                                        <tr>

                                            <th>DNI</th>
                                            <th>Nombres</th>
                                            <th>Apellidos</th>
                                            <th>F. Nacimiento</th>
                                            <th>Edad</th>
                                            <th>Teléfono</th>
                                            <th>Correo</th>
                                            <th>Dirección</th>
                                            <th>Distrito</th>
                                            <th>Acciones</th>

                                        </tr>

                                    </thead>


                                    <tbody>

                                        {
                                            personas.map(
                                                (persona) => (

                                                    <tr
                                                        key={
                                                            persona.id_persona
                                                        }
                                                    >

                                                        <td>
                                                            {persona.dni}
                                                        </td>

                                                        <td>
                                                            {persona.nombres}
                                                        </td>

                                                        <td>
                                                            {persona.apellidos}
                                                        </td>

                                                        <td>
                                                            {
                                                                persona.fecha_nacimiento ||
                                                                "-"
                                                            }
                                                        </td>

                                                        <td>

                                                            {
                                                                persona.edad !== null &&
                                                                persona.edad !== undefined

                                                                    ? `${persona.edad} años`

                                                                    : "-"
                                                            }

                                                        </td>

                                                        <td>
                                                            {
                                                                persona.telefono ||
                                                                "-"
                                                            }
                                                        </td>

                                                        <td>
                                                            {
                                                                persona.correo ||
                                                                "-"
                                                            }
                                                        </td>

                                                        <td>
                                                            {
                                                                persona.direccion ||
                                                                "-"
                                                            }
                                                        </td>

                                                        <td>
                                                            {
                                                                persona.distrito ||
                                                                "-"
                                                            }
                                                        </td>


                                                        <td>

                                                            <div className="d-flex gap-2">

                                                                <button
                                                                    type="button"
                                                                    className="btn btn-warning btn-sm"
                                                                    onClick={
                                                                        () =>
                                                                            editarPersona(
                                                                                persona
                                                                            )
                                                                    }
                                                                >
                                                                    Editar
                                                                </button>

                                                                <button
                                                                    type="button"
                                                                    className="btn btn-danger btn-sm"
                                                                    onClick={
                                                                        () =>
                                                                            eliminarPersona(
                                                                                persona.id_persona
                                                                            )
                                                                    }
                                                                >
                                                                    Eliminar
                                                                </button>

                                                            </div>

                                                        </td>

                                                    </tr>

                                                )
                                            )
                                        }

                                    </tbody>

                                </table>

                            </div>

                        )
                    }

                </div>

            </div>

        </div>
    );
}


export default Personas;