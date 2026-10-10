import { useEffect, useState } from "react";
import api from "../../api/axios";
import Busqueda from "../../components/busqueda/Busqueda";
import "../../components/busqueda/busqueda.css";

import "./distritos.css";

import {
    alertaExito,
    alertaError,
    alertaAdvertencia,
    confirmarAccion
} from "../../utils/alertas";

const API_URL = "/distritos/";

function Distritos() {

    // =========================================================
    // ESTADOS
    // =========================================================

    const [distritos, setDistritos] = useState([]);

    const [mostrarFormulario, setMostrarFormulario] = useState(false);

    const [nombre, setNombre] = useState("");

    const [editando, setEditando] = useState(null);

    const [cargando, setCargando] = useState(true);
    const [busqueda, setBusqueda] = useState({ id: "", nombre: "" });

    // =========================================================
    // OBTENER DISTRITOS
    // =========================================================

    const cargarDistritos = async () => {

        try {

            setCargando(true);

            const respuesta = await api.get(API_URL);

            setDistritos(respuesta.data);

        } catch (error) {

            console.error(
                "Error al obtener distritos:",
                error
            );

            alertaError(
                error.response?.data?.detail ||
                "No se pudieron obtener los distritos desde la API."
            );

        } finally {

            setCargando(false);

        }

    };

    // =========================================================
    // CARGAR AL INICIAR
    // =========================================================

    useEffect(() => {

        cargarDistritos();

    }, []);

    const buscarDistritos = async (e) => {
        e.preventDefault();
        if (!busqueda.id && !busqueda.nombre.trim()) {
            await cargarDistritos();
            return;
        }
        try {
            setCargando(true);
            const params = {};
            if (busqueda.id) params.id = Number(busqueda.id);
            if (busqueda.nombre.trim()) params.nombre = busqueda.nombre.trim();
            const respuesta = await api.get(`${API_URL}buscar`, { params });
            setDistritos(respuesta.data);
        } catch (error) {
            alertaError(error.response?.data?.detail || "No se pudieron buscar los distritos.");
        } finally {
            setCargando(false);
        }
    };

    const limpiarBusqueda = async () => {
        setBusqueda({ id: "", nombre: "" });
        await cargarDistritos();
    };

    // =========================================================
    // LIMPIAR FORMULARIO
    // =========================================================

    const limpiarFormulario = () => {

        setNombre("");

        setEditando(null);

    };

    // =========================================================
    // MOSTRAR / OCULTAR FORMULARIO
    // =========================================================

    const cambiarFormulario = () => {

        setMostrarFormulario(!mostrarFormulario);

        if (mostrarFormulario) {

            limpiarFormulario();

        }

    };

    // =========================================================
    // GUARDAR DISTRITO
    // =========================================================

    const guardarDistrito = async (e) => {

        e.preventDefault();

        const nombreLimpio = nombre.trim();

        // =====================================================
        // VALIDACIÓN
        // =====================================================

        if (nombreLimpio === "") {

            alertaAdvertencia(
                "El nombre del distrito es obligatorio."
            );

            return;

        }

        try {

            // =================================================
            // ACTUALIZAR
            // =================================================

            if (editando !== null) {

                await api.put(
                    `${API_URL}${editando}`,
                    {
                        nombre: nombreLimpio
                    }
                );

                alertaExito(
                    "Distrito actualizado correctamente."
                );

            }

            // =================================================
            // CREAR
            // =================================================

            else {

                await api.post(
                    API_URL,
                    {
                        nombre: nombreLimpio
                    }
                );

                alertaExito(
                    "Distrito registrado correctamente."
                );

            }

            limpiarFormulario();

            await cargarDistritos();

            setMostrarFormulario(false);

        } catch (error) {

            console.error(
                "Error al guardar distrito:",
                error
            );

            alertaError(
                error.response?.data?.detail ||
                "No se pudo guardar el distrito."
            );

        }

    };

    // =========================================================
    // EDITAR DISTRITO
    // =========================================================

    const editarDistrito = (distrito) => {

        setEditando(distrito.id_distrito);

        setNombre(distrito.nombre);

        setMostrarFormulario(true);

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });

    };

    // =========================================================
    // ELIMINAR DISTRITO
    // =========================================================

    const eliminarDistrito = async (id) => {

        const confirmado = await confirmarAccion(
            `¿Está seguro de eliminar el distrito ID=${id}?`
        );

        if (!confirmado) {

            return;

        }

        try {

            await api.delete(
                `${API_URL}${id}`
            );

            alertaExito(
                "Distrito eliminado correctamente."
            );

            await cargarDistritos();

        } catch (error) {

            console.error(
                "Error al eliminar distrito:",
                error
            );

            alertaError(
                error.response?.data?.detail ||
                "No se pudo eliminar el distrito."
            );

        }

    };

    // =========================================================
    // INTERFAZ
    // =========================================================

    return (

        <div className="distritos-page container-fluid px-3 px-md-4 mt-4">

            {/* =================================================
                TÍTULO
            ================================================= */}

            <div className="d-flex justify-content-between align-items-center mb-4">

                <div>

                    <h1 className="mb-1">
                        Distritos
                    </h1>

                    <p className="text-muted mb-0">
                        Gestión de distritos registrados
                    </p>

                </div>
                <span className="page-count-badge">
                    {distritos.length}
                </span>

            </div>

            {/* =================================================
                BOTÓN REGISTRAR / OCULTAR
            ================================================= */}

            <Busqueda
                campos={[
                    { name: "id", label: "ID", type: "number", placeholder: "Ej: 1", value: busqueda.id, onChange: (e) => setBusqueda({ ...busqueda, id: e.target.value }) },
                    { name: "nombre", label: "Distrito", placeholder: "Ej: Miraflores", value: busqueda.nombre, onChange: (e) => setBusqueda({ ...busqueda, nombre: e.target.value }) }
                ]}
                onBuscar={buscarDistritos}
                onLimpiar={limpiarBusqueda}
                cargando={cargando}
            />

            <div className="d-flex justify-content-end mb-4">

                <button
                    type="button"
                    className="btn btn-primary"
                    onClick={cambiarFormulario}
                >
                    {mostrarFormulario
                        ? "− Ocultar registro"
                        : "＋ Registrar distrito"}
                </button>

            </div>

            {/* =================================================
                FORMULARIO
            ================================================= */}

            {mostrarFormulario && (

                <div className="card shadow-sm mb-4">

                    <div className="card-body">

                        <h4 className="mb-4">

                            {editando !== null
                                ? "Editar Distrito"
                                : "Registrar Distrito"}

                        </h4>

                        <form onSubmit={guardarDistrito}>

                            <div className="row align-items-end">

                                {/* NOMBRE */}

                                <div className="col-md-8">

                                    <label
                                        htmlFor="nombreDistrito"
                                        className="form-label"
                                    >
                                        Nombre del Distrito{" "}

                                        <span className="text-danger">
                                            *
                                        </span>

                                    </label>

                                    <input
                                        id="nombreDistrito"
                                        type="text"
                                        className="form-control"
                                        placeholder="Ej: Miraflores"
                                        value={nombre}
                                        onChange={(e) =>
                                            setNombre(e.target.value)
                                        }
                                        required
                                    />

                                </div>

                                {/* BOTONES */}

                                <div className="col-md-4 mt-3 mt-md-0">

                                    <div className="d-flex gap-2">

                                        <button
                                            type="submit"
                                            className="btn btn-primary"
                                        >
                                            {editando !== null
                                                ? "Actualizar"
                                                : "Guardar"}
                                        </button>

                                        <button
                                            type="button"
                                            className="btn btn-secondary"
                                            onClick={limpiarFormulario}
                                        >
                                            Limpiar
                                        </button>

                                    </div>

                                </div>

                            </div>

                        </form>

                    </div>

                </div>

            )}

            {/* =================================================
                LISTA DE DISTRITOS
            ================================================= */}

            <div className="card shadow-sm">

                <div className="card-body">

                    <h4 className="mb-4">
                        Distritos registrados
                    </h4>

                    {/* CARGANDO */}

                    {cargando && (

                        <div className="text-center py-4">

                            <div
                                className="spinner-border text-primary"
                                role="status"
                            >
                                <span className="visually-hidden">
                                    Cargando...
                                </span>
                            </div>

                            <p className="text-muted mt-2">
                                Cargando distritos...
                            </p>

                        </div>

                    )}

                    {/* SIN DISTRITOS */}

                    {!cargando &&
                        distritos.length === 0 && (

                            <div className="alert alert-info">
                                No existen distritos registrados.
                            </div>

                        )}

                    {/* TABLA */}

                    {!cargando &&
                        distritos.length > 0 && (

                            <div className="table-responsive">

                                <table className="table table-hover align-middle">

                                    <thead className="table-light">

                                        <tr>

                                            <th>
                                                ID
                                            </th>

                                            <th>
                                                Nombre
                                            </th>

                                            <th className="text-center">
                                                Acciones
                                            </th>

                                        </tr>

                                    </thead>

                                    <tbody>

                                        {distritos.map((distrito) => (

                                            <tr
                                                key={distrito.id_distrito}
                                            >

                                                <td>
                                                    {distrito.id_distrito}
                                                </td>

                                                <td>

                                                    <strong>
                                                        {distrito.nombre}
                                                    </strong>

                                                </td>

                                                <td className="text-center">

                                                    <div className="d-flex justify-content-center gap-2">

                                                        <button
                                                            type="button"
                                                            className="btn btn-sm btn-warning"
                                                            onClick={() =>
                                                                editarDistrito(
                                                                    distrito
                                                                )
                                                            }
                                                        >
                                                            Editar
                                                        </button>

                                                        <button
                                                            type="button"
                                                            className="btn btn-sm btn-danger"
                                                            onClick={() =>
                                                                eliminarDistrito(
                                                                    distrito.id_distrito
                                                                )
                                                            }
                                                        >
                                                            Eliminar
                                                        </button>

                                                    </div>

                                                </td>

                                            </tr>

                                        ))}

                                    </tbody>

                                </table>

                            </div>

                        )}

                </div>

            </div>

        </div>

    );

}

export default Distritos;
