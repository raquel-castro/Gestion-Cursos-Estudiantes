import { useEffect, useState } from "react";
import api from "../../api/axios";
import Busqueda from "../../components/busqueda/Busqueda";
import "../../components/busqueda/busqueda.css";
import "./docentes.css";
import {
    alertaExito,
    alertaError,
    alertaAdvertencia,
    confirmarAccion
} from "../../utils/alertas";

const API_DOCENTES = "/docentes/";
const API_PERSONAS = "/personas/";

function Docentes() {
    const [docentes, setDocentes] = useState([]);
    const [personas, setPersonas] = useState([]);
    const [mostrarFormulario, setMostrarFormulario] = useState(false);
    const [especialidad, setEspecialidad] = useState("");
    const [persona, setPersona] = useState("");
    const [editando, setEditando] = useState(null);
    const [cargando, setCargando] = useState(true);
    const [busqueda, setBusqueda] = useState({ id: "", especialidad: "", nombre: "" });

    const cargarDatos = async () => {
        try {
            setCargando(true);
            const [respuestaDocentes, respuestaPersonas] = await Promise.all([
                api.get(API_DOCENTES),
                api.get(API_PERSONAS)
            ]);
            setDocentes(respuestaDocentes.data);
            setPersonas(respuestaPersonas.data);
        } catch (error) {
            console.error("Error al cargar datos:", error);
            alertaError(
                error.response?.data?.detail ||
                "No se pudieron cargar los docentes."
            );
        } finally {
            setCargando(false);
        }
    };

    useEffect(() => {
        cargarDatos();
    }, []);

    const buscarDocentes = async (e) => {
        e.preventDefault();
        const params = Object.fromEntries(
            Object.entries(busqueda).filter(([, value]) => value.trim() !== "")
        );
        if (Object.keys(params).length === 0) {
            await cargarDatos();
            return;
        }
        try {
            setCargando(true);
            const respuesta = await api.get(`${API_DOCENTES}buscar`, { params });
            setDocentes(respuesta.data);
        } catch (error) {
            alertaError(error.response?.data?.detail || "No se pudieron buscar los docentes.");
        } finally {
            setCargando(false);
        }
    };

    const limpiarBusqueda = async () => {
        setBusqueda({ id: "", especialidad: "", nombre: "" });
        await cargarDatos();
    };

    const limpiarFormulario = () => {
        setEspecialidad("");
        setPersona("");
        setEditando(null);
    };

    const cambiarFormulario = () => {
        if (mostrarFormulario) limpiarFormulario();
        setMostrarFormulario(!mostrarFormulario);
    };

    const guardarDocente = async (e) => {
        e.preventDefault();
        const especialidadLimpia = especialidad.trim();

        if (especialidadLimpia === "") {
            alertaAdvertencia("La especialidad es obligatoria.");
            return;
        }

        if (persona === "") {
            alertaAdvertencia("Debe seleccionar una persona.");
            return;
        }

        try {
            const datos = {
                especialidad: especialidadLimpia,
                id_persona: Number(persona)
            };

            if (editando !== null) {
                await api.put(`${API_DOCENTES}${editando}`, datos);
                alertaExito("Docente actualizado correctamente.");
            } else {
                await api.post(API_DOCENTES, datos);
                alertaExito("Docente registrado correctamente.");
            }

            limpiarFormulario();
            setMostrarFormulario(false);
            await cargarDatos();
        } catch (error) {
            console.error("Error al guardar docente:", error);
            alertaError(
                error.response?.data?.detail ||
                "No se pudo guardar el docente."
            );
        }
    };

    const editarDocente = (docente) => {
        setEspecialidad(docente.especialidad);
        setPersona(String(docente.id_persona));
        setEditando(docente.id_docente);
        setMostrarFormulario(true);
        window.scrollTo({ top: 0, behavior: "smooth" });
    };

    const eliminarDocente = async (id) => {
        const confirmado = await confirmarAccion(
            `¿Está seguro de eliminar el docente ID=${id}?`
        );

        if (!confirmado) return;

        try {
            await api.delete(`${API_DOCENTES}${id}`);
            alertaExito("Docente eliminado correctamente.");
            await cargarDatos();
        } catch (error) {
            console.error("Error al eliminar docente:", error);
            alertaError(
                error.response?.data?.detail ||
                "No se pudo eliminar el docente."
            );
        }
    };

    const obtenerNombrePersona = (id) => {
        const personaEncontrada = personas.find(
            p => p.id_persona === id
        );
        return personaEncontrada
            ? `${personaEncontrada.nombres} ${personaEncontrada.apellidos}`
            : `ID ${id}`;
    };

    const obtenerDniPersona = (id) => {
        const personaEncontrada = personas.find(
            p => p.id_persona === id
        );
        return personaEncontrada?.dni || "—";
    };

    return (
        <div className="docentes-page container-fluid px-3 px-md-4 mt-4">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h1 className="mb-1">Registro de Docente</h1>
                    <p className="text-muted mb-0">
                        Gestión de docentes registrados
                    </p>
                </div>

                <span className="page-count-badge">
                    {docentes.length}
                </span>
            </div>

            <Busqueda
                campos={[
                    { name: "id", label: "ID", type: "number", placeholder: "Ej: 1", value: busqueda.id, onChange: (e) => setBusqueda({ ...busqueda, id: e.target.value }) },
                    { name: "especialidad", label: "Especialidad", placeholder: "Ej: Programación", value: busqueda.especialidad, onChange: (e) => setBusqueda({ ...busqueda, especialidad: e.target.value }) },
                    { name: "nombre", label: "Docente", placeholder: "Ej: Sofia", value: busqueda.nombre, onChange: (e) => setBusqueda({ ...busqueda, nombre: e.target.value }) }
                ]}
                onBuscar={buscarDocentes}
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
                        : "＋ Registrar docente"}
                </button>
            </div>

            {mostrarFormulario && (
                <div className="card shadow-sm">
                    <div className="card-body">
                        <h4 className="mb-4">
                            {editando !== null
                                ? "Editar Docente"
                                : "Información del Docente"}
                        </h4>

                        <form onSubmit={guardarDocente}>
                            <div className="row">
                                <div className="col-md-6 mb-3">
                                    <label
                                        className="form-label"
                                        htmlFor="especialidad"
                                    >
                                        Especialidad{" "}
                                        <span className="text-danger">*</span>
                                    </label>

                                    <input
                                        id="especialidad"
                                        type="text"
                                        className="form-control"
                                        placeholder="Ej: Base de Datos"
                                        value={especialidad}
                                        onChange={e =>
                                            setEspecialidad(e.target.value)
                                        }
                                        required
                                    />
                                </div>

                                <div className="col-md-6 mb-3">
                                    <label
                                        className="form-label"
                                        htmlFor="persona"
                                    >
                                        Persona{" "}
                                        <span className="text-danger">*</span>
                                    </label>

                                    <select
                                        id="persona"
                                        className="form-select"
                                        value={persona}
                                        onChange={e =>
                                            setPersona(e.target.value)
                                        }
                                        required
                                    >
                                        <option value="">
                                            Seleccione una persona
                                        </option>

                                        {personas.map(p => (
                                            <option
                                                key={p.id_persona}
                                                value={p.id_persona}
                                            >
                                                {p.nombres} {p.apellidos} - DNI {p.dni}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>

                            <div className="mt-3">
                                <button
                                    type="button"
                                    className="btn btn-secondary me-2"
                                    onClick={limpiarFormulario}
                                >
                                    Limpiar
                                </button>

                                <button
                                    type="submit"
                                    className="btn btn-primary"
                                >
                                    {editando !== null
                                        ? "Actualizar Docente"
                                        : "Guardar Docente"}
                                </button>
                            </div>
                        </form>
                    </div>
                </div>
            )}

            <div className="card shadow-sm mt-4">
                <div className="card-body">
                    <h4 className="mb-4">
                        Docentes Registrados
                    </h4>

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
                                Cargando docentes...
                            </p>
                        </div>
                    )}

                    {!cargando && docentes.length === 0 && (
                        <div className="alert alert-info">
                            No hay docentes registrados.
                        </div>
                    )}

                    {!cargando && docentes.length > 0 && (
                        <div className="table-responsive">
                            <table className="table table-hover align-middle">
                                <thead className="table-light">
                                    <tr>
                                        <th>ID</th>
                                        <th>Especialidad</th>
                                        <th>Persona</th>
                                        <th>DNI</th>
                                        <th className="text-center">
                                            Acciones
                                        </th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {docentes.map(docente => (
                                        <tr key={docente.id_docente}>
                                            <td>{docente.id_docente}</td>

                                            <td>
                                                <strong>
                                                    {docente.especialidad}
                                                </strong>
                                            </td>

                                            <td>
                                                {obtenerNombrePersona(
                                                    docente.id_persona
                                                )}
                                            </td>

                                            <td>
                                                {obtenerDniPersona(
                                                    docente.id_persona
                                                )}
                                            </td>

                                            <td className="text-center">
                                                <button
                                                    type="button"
                                                    className="btn btn-warning btn-sm me-2"
                                                    onClick={() =>
                                                        editarDocente(docente)
                                                    }
                                                >
                                                    Editar
                                                </button>

                                                <button
                                                    type="button"
                                                    className="btn btn-danger btn-sm"
                                                    onClick={() =>
                                                        eliminarDocente(
                                                            docente.id_docente
                                                        )
                                                    }
                                                >
                                                    Eliminar
                                                </button>
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

export default Docentes;
