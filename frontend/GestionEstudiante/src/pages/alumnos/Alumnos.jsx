import { useEffect, useState } from "react";
import api from "../../api/axios";
import Busqueda from "../../components/busqueda/Busqueda";
import "../../components/busqueda/busqueda.css";
import "./alumnos.css";
import {
    alertaExito,
    alertaError,
    alertaAdvertencia,
    confirmarAccion
} from "../../utils/alertas";

const API_URL = "/alumnos/";
const PERSONAS_URL = "/personas/";
const DISTRITOS_URL = "/distritos/";

function Alumnos() {
    const [alumnos, setAlumnos] = useState([]);
    const [personas, setPersonas] = useState([]);
    const [distritos, setDistritos] = useState([]);
    const [mostrarFormulario, setMostrarFormulario] = useState(false);
    const [codigo, setCodigo] = useState("");
    const [idPersona, setIdPersona] = useState("");
    const [idDistrito, setIdDistrito] = useState("");
    const [editando, setEditando] = useState(null);
    const [cargando, setCargando] = useState(true);
    const [busqueda, setBusqueda] = useState({ id: "", codigo: "", dni: "", nombre: "", distrito: "" });

    const cargarDatos = async () => {
        try {
            setCargando(true);

            const [a, p, d] = await Promise.all([
                api.get(API_URL),
                api.get(PERSONAS_URL),
                api.get(DISTRITOS_URL)
            ]);

            setAlumnos(a.data);
            setPersonas(p.data);
            setDistritos(d.data);
        } catch (error) {
            console.error("Error al cargar datos:", error);
            alertaError(
                error.response?.data?.detail ||
                "No se pudieron cargar los datos."
            );
        } finally {
            setCargando(false);
        }
    };

    useEffect(() => {
        cargarDatos();
    }, []);

    const buscarAlumnos = async (e) => {
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
            const respuesta = await api.get(`${API_URL}buscar`, { params });
            setAlumnos(respuesta.data);
        } catch (error) {
            alertaError(error.response?.data?.detail || "No se pudieron buscar los alumnos.");
        } finally {
            setCargando(false);
        }
    };

    const limpiarBusqueda = async () => {
        setBusqueda({ id: "", codigo: "", dni: "", nombre: "", distrito: "" });
        await cargarDatos();
    };

    const limpiarFormulario = () => {
        setCodigo("");
        setIdPersona("");
        setIdDistrito("");
        setEditando(null);
    };

    const cambiarFormulario = () => {
        if (mostrarFormulario) limpiarFormulario();
        setMostrarFormulario(!mostrarFormulario);
    };

    const guardarAlumno = async (e) => {
        e.preventDefault();

        if (!codigo.trim()) {
            alertaAdvertencia("Ingrese el código del alumno.");
            return;
        }

        if (!idPersona) {
            alertaAdvertencia("Seleccione una persona.");
            return;
        }

        if (!idDistrito) {
            alertaAdvertencia("Seleccione un distrito.");
            return;
        }

        const datos = {
            codigo_alumno: codigo.trim(),
            id_persona: Number(idPersona),
            id_distrito: Number(idDistrito)
        };

        try {
            if (editando) {
                await api.put(`${API_URL}${editando}`, datos);
                alertaExito("Alumno actualizado correctamente.");
            } else {
                await api.post(API_URL, datos);
                alertaExito("Alumno registrado correctamente.");
            }

            limpiarFormulario();
            setMostrarFormulario(false);
            cargarDatos();
        } catch (error) {
            console.error("Error al guardar alumno:", error);
            alertaError(
                error.response?.data?.detail ||
                "No se pudo guardar el alumno."
            );
        }
    };

    const editarAlumno = (alumno) => {
        setCodigo(alumno.codigo_alumno);
        setIdPersona(String(alumno.id_persona));
        setIdDistrito(String(alumno.id_distrito));
        setEditando(alumno.id_alumno);
        setMostrarFormulario(true);
    };

    const eliminarAlumno = async (id) => {
        const confirmado = await confirmarAccion(
            `¿Está seguro de eliminar el alumno ID=${id}?`
        );

        if (!confirmado) return;

        try {
            await api.delete(`${API_URL}${id}`);
            alertaExito("Alumno eliminado correctamente.");
            cargarDatos();
        } catch (error) {
            console.error("Error al eliminar alumno:", error);
            alertaError(
                error.response?.data?.detail ||
                "No se pudo eliminar el alumno."
            );
        }
    };

    const obtenerPersona = (id) => {
        const p = personas.find(x => x.id_persona === id);
        return p ? `${p.nombres} ${p.apellidos}` : `ID ${id}`;
    };

    const obtenerDni = (id) => {
        const p = personas.find(x => x.id_persona === id);
        return p?.dni || "—";
    };

    const obtenerDistrito = (id) => {
        const d = distritos.find(x => x.id_distrito === id);
        return d?.nombre || `ID ${id}`;
    };

    return (
        <div className="alumnos-page container-fluid">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h1>Alumnos</h1>
                    <p className="text-muted">
                        Gestión de alumnos registrados
                    </p>
                </div>
                <span className="page-count-badge">
                    {alumnos.length}
                </span>
            </div>

            <Busqueda
                campos={[
                    { name: "id", label: "ID", type: "number", placeholder: "Ej: 1", value: busqueda.id, onChange: (e) => setBusqueda({ ...busqueda, id: e.target.value }) },
                    { name: "codigo", label: "Código", placeholder: "Ej: ALU2026001", value: busqueda.codigo, onChange: (e) => setBusqueda({ ...busqueda, codigo: e.target.value }) },
                    { name: "dni", label: "DNI", placeholder: "Ej: 71234567", value: busqueda.dni, onChange: (e) => setBusqueda({ ...busqueda, dni: e.target.value }) },
                    { name: "nombre", label: "Nombre", placeholder: "Ej: Carlos", value: busqueda.nombre, onChange: (e) => setBusqueda({ ...busqueda, nombre: e.target.value }) },
                    { name: "distrito", label: "Distrito", placeholder: "Ej: Miraflores", value: busqueda.distrito, onChange: (e) => setBusqueda({ ...busqueda, distrito: e.target.value }) }
                ]}
                onBuscar={buscarAlumnos}
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
                        : "＋ Registrar alumno"}
                </button>
            </div>

            {mostrarFormulario && (
                <div className="card shadow-sm mb-4">
                    <div className="card-body">
                        <h4 className="mb-4">
                            {editando ? "Editar Alumno" : "Registrar Alumno"}
                        </h4>

                        <form onSubmit={guardarAlumno}>
                            <div className="row">
                                <div className="col-md-4 mb-3">
                                    <label className="form-label">
                                        Código de Alumno *
                                    </label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        placeholder="Ej: ALU2026001"
                                        value={codigo}
                                        onChange={(e) =>
                                            setCodigo(e.target.value)
                                        }
                                        required
                                    />
                                </div>

                                <div className="col-md-4 mb-3">
                                    <label className="form-label">
                                        Persona *
                                    </label>
                                    <select
                                        className="form-select"
                                        value={idPersona}
                                        onChange={(e) =>
                                            setIdPersona(e.target.value)
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

                                <div className="col-md-4 mb-3">
                                    <label className="form-label">
                                        Distrito *
                                    </label>
                                    <select
                                        className="form-select"
                                        value={idDistrito}
                                        onChange={(e) =>
                                            setIdDistrito(e.target.value)
                                        }
                                        required
                                    >
                                        <option value="">
                                            Seleccione un distrito
                                        </option>
                                        {distritos.map(d => (
                                            <option
                                                key={d.id_distrito}
                                                value={d.id_distrito}
                                            >
                                                {d.nombre}
                                            </option>
                                        ))}
                                    </select>
                                </div>
                            </div>

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
                                {editando
                                    ? "Actualizar Alumno"
                                    : "Guardar Alumno"}
                            </button>
                        </form>
                    </div>
                </div>
            )}

            <div className="card shadow-sm">
                <div className="card-body">
                    <h4 className="mb-4">
                        Alumnos registrados
                    </h4>

                    {cargando ? (
                        <div className="text-center py-4">
                            <div
                                className="spinner-border text-primary"
                                role="status"
                            />
                            <p className="text-muted mt-2">
                                Cargando alumnos...
                            </p>
                        </div>
                    ) : alumnos.length === 0 ? (
                        <div className="alert alert-info">
                            No hay alumnos registrados.
                        </div>
                    ) : (
                        <div className="table-responsive">
                            <table className="table table-hover align-middle">
                                <thead className="table-light">
                                    <tr>
                                        <th>ID</th>
                                        <th>Código</th>
                                        <th>Persona</th>
                                        <th>DNI</th>
                                        <th>Distrito</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {alumnos.map(alumno => (
                                        <tr key={alumno.id_alumno}>
                                            <td>{alumno.id_alumno}</td>
                                            <td>
                                                <strong>
                                                    {alumno.codigo_alumno}
                                                </strong>
                                            </td>
                                            <td>
                                                {obtenerPersona(
                                                    alumno.id_persona
                                                )}
                                            </td>
                                            <td>
                                                {obtenerDni(
                                                    alumno.id_persona
                                                )}
                                            </td>
                                            <td>
                                                {obtenerDistrito(
                                                    alumno.id_distrito
                                                )}
                                            </td>
                                            <td>
                                                <button
                                                    type="button"
                                                    className="btn btn-warning btn-sm me-2"
                                                    onClick={() =>
                                                        editarAlumno(alumno)
                                                    }
                                                >
                                                    Editar
                                                </button>

                                                <button
                                                    type="button"
                                                    className="btn btn-danger btn-sm"
                                                    onClick={() =>
                                                        eliminarAlumno(
                                                            alumno.id_alumno
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

export default Alumnos;
