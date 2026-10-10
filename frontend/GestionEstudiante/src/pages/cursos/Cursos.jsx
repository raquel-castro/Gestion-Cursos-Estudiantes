import { useEffect, useState } from "react";
import api from "../../api/axios";
import Busqueda from "../../components/busqueda/Busqueda";
import "../../components/busqueda/busqueda.css";
import "./cursos.css";
import {
    alertaExito,
    alertaError,
    alertaAdvertencia,
    confirmarAccion
} from "../../utils/alertas";

const API_URL = "/cursos/";
const DOCENTES_URL = "/docentes/";

function Cursos() {
    const [cursos, setCursos] = useState([]);
    const [docentes, setDocentes] = useState([]);
    const [mostrarFormulario, setMostrarFormulario] = useState(false);
    const [nombre, setNombre] = useState("");
    const [descripcion, setDescripcion] = useState("");
    const [creditos, setCreditos] = useState("");
    const [ciclo, setCiclo] = useState("");
    const [horas, setHoras] = useState("");
    const [docente, setDocente] = useState("");
    const [editando, setEditando] = useState(null);
    const [cargando, setCargando] = useState(true);
    const [busqueda, setBusqueda] = useState({ id: "", nombre: "", ciclo: "", id_docente: "" });

    const cargarDatos = async () => {
        try {
            setCargando(true);
            const [c, d] = await Promise.all([
                api.get(API_URL),
                api.get(DOCENTES_URL)
            ]);
            setCursos(c.data);
            setDocentes(d.data);
        } catch (error) {
            console.error("Error al cargar cursos:", error);
            alertaError(
                error.response?.data?.detail ||
                "No se pudieron cargar los cursos."
            );
        } finally {
            setCargando(false);
        }
    };

    useEffect(() => {
        cargarDatos();
    }, []);

    const buscarCursos = async (e) => {
        e.preventDefault();
        const params = {};
        if (busqueda.id) params.id = Number(busqueda.id);
        if (busqueda.nombre.trim()) params.nombre = busqueda.nombre.trim();
        if (busqueda.ciclo.trim()) params.ciclo = busqueda.ciclo.trim();
        if (busqueda.id_docente) params.id_docente = Number(busqueda.id_docente);
        if (Object.keys(params).length === 0) {
            await cargarDatos();
            return;
        }
        try {
            setCargando(true);
            const respuesta = await api.get(`${API_URL}buscar`, { params });
            setCursos(respuesta.data);
        } catch (error) {
            alertaError(error.response?.data?.detail || "No se pudieron buscar los cursos.");
        } finally {
            setCargando(false);
        }
    };

    const limpiarBusqueda = async () => {
        setBusqueda({ id: "", nombre: "", ciclo: "", id_docente: "" });
        await cargarDatos();
    };

    const limpiarFormulario = () => {
        setNombre("");
        setDescripcion("");
        setCreditos("");
        setCiclo("");
        setHoras("");
        setDocente("");
        setEditando(null);
    };

    const cambiarFormulario = () => {
        if (mostrarFormulario) limpiarFormulario();
        setMostrarFormulario(!mostrarFormulario);
    };

    const guardarCurso = async (e) => {
        e.preventDefault();

        const nombreLimpio = nombre.trim();
        const descripcionLimpia = descripcion.trim();

        if (!nombreLimpio) {
            alertaAdvertencia("El nombre del curso es obligatorio.");
            return;
        }

        if (/^\d+$/.test(nombreLimpio)) {
            alertaAdvertencia("El nombre del curso debe contener letras.");
            return;
        }

        if (!descripcionLimpia) {
            alertaAdvertencia("La descripción es obligatoria.");
            return;
        }

        if (/^\d+$/.test(descripcionLimpia)) {
            alertaAdvertencia("La descripción debe contener letras.");
            return;
        }

        if (creditos === "") {
            alertaAdvertencia("Los créditos son obligatorios.");
            return;
        }

        if (!/^\d+$/.test(creditos)) {
            alertaAdvertencia("Los créditos deben ser un número.");
            return;
        }

        const creditosNumero = Number(creditos);

        if (creditosNumero < 1 || creditosNumero > 9) {
            alertaAdvertencia("Los créditos deben estar entre 1 y 9.");
            return;
        }

        if (!ciclo) {
            alertaAdvertencia("Debe seleccionar un ciclo.");
            return;
        }

        if (horas === "") {
            alertaAdvertencia("Las horas semanales son obligatorias.");
            return;
        }

        if (!/^\d+$/.test(horas)) {
            alertaAdvertencia("Las horas semanales deben ser un número.");
            return;
        }

        const horasNumero = Number(horas);

        if (horasNumero < 1 || horasNumero > 40) {
            alertaAdvertencia("Las horas semanales deben estar entre 1 y 40.");
            return;
        }

        if (!docente) {
            alertaAdvertencia("Debe seleccionar un docente.");
            return;
        }

        const datos = {
            nombre: nombreLimpio,
            descripcion: descripcionLimpia,
            creditos: creditosNumero,
            ciclo,
            horas_semanales: horasNumero,
            id_docente: Number(docente)
        };

        try {
            if (editando !== null) {
                await api.put(`${API_URL}${editando}`, datos);
                alertaExito("Curso actualizado correctamente.");
            } else {
                await api.post(API_URL, datos);
                alertaExito("Curso registrado correctamente.");
            }

            limpiarFormulario();
            setMostrarFormulario(false);
            await cargarDatos();
        } catch (error) {
            console.error("Error al guardar curso:", error);
            alertaError(
                error.response?.data?.detail ||
                "No se pudo guardar el curso."
            );
        }
    };

    const editarCurso = (curso) => {
        setNombre(curso.nombre);
        setDescripcion(curso.descripcion || "");
        setCreditos(String(curso.creditos));
        setCiclo(curso.ciclo);
        setHoras(String(curso.horas_semanales));
        setDocente(String(curso.id_docente));
        setEditando(curso.id_curso);
        setMostrarFormulario(true);
    };

    const eliminarCurso = async (id) => {
        const confirmado = await confirmarAccion(
            `¿Está seguro de eliminar el curso ID=${id}?`
        );

        if (!confirmado) return;

        try {
            await api.delete(`${API_URL}${id}`);
            alertaExito("Curso eliminado correctamente.");
            await cargarDatos();
        } catch (error) {
            console.error("Error al eliminar curso:", error);
            alertaError(
                error.response?.data?.detail ||
                "No se pudo eliminar el curso."
            );
        }
    };

    const obtenerDocente = (id) => {
        const d = docentes.find(x => x.id_docente === id);
        return d ? `ID ${d.id_docente} - ${d.especialidad}` : `ID ${id}`;
    };

    return (
        <div className="cursos-page container-fluid">
            <div className="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h1>Registro de Curso</h1>
                    <p className="text-muted">
                        Gestión de cursos registrados
                    </p>
                </div>
                <span className="page-count-badge">
                    {cursos.length}
                </span>
            </div>

            <Busqueda
                campos={[
                    { name: "id", label: "ID", type: "number", placeholder: "Ej: 1", value: busqueda.id, onChange: (e) => setBusqueda({ ...busqueda, id: e.target.value }) },
                    { name: "nombre", label: "Curso", placeholder: "Ej: Programación", value: busqueda.nombre, onChange: (e) => setBusqueda({ ...busqueda, nombre: e.target.value }) },
                    { name: "ciclo", label: "Ciclo", placeholder: "Ej: III", value: busqueda.ciclo, onChange: (e) => setBusqueda({ ...busqueda, ciclo: e.target.value }) },
                    { name: "id_docente", label: "Docente", type: "select", value: busqueda.id_docente, onChange: (e) => setBusqueda({ ...busqueda, id_docente: e.target.value }), options: [{ value: "", label: "Todos los docentes" }, ...docentes.map((d) => ({ value: String(d.id_docente), label: `Docente ${d.id_docente} - ${d.especialidad}` }))] }
                ]}
                onBuscar={buscarCursos}
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
                        : "＋ Registrar curso"}
                </button>
            </div>

            {mostrarFormulario && (
                <div className="card shadow-sm mb-4">
                    <div className="card-body">
                        <h4 className="mb-4">
                            {editando !== null
                                ? "Editar Curso"
                                : "Información del Curso"}
                        </h4>

                        <form onSubmit={guardarCurso}>
                            <div className="row">
                                <div className="col-md-6 mb-3">
                                    <label className="form-label">
                                        Nombre del Curso *
                                    </label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        placeholder="Ej: Base de Datos"
                                        value={nombre}
                                        onChange={e =>
                                            setNombre(e.target.value)
                                        }
                                        required
                                    />
                                </div>

                                <div className="col-md-6 mb-3">
                                    <label className="form-label">
                                        Descripción *
                                    </label>
                                    <input
                                        type="text"
                                        className="form-control"
                                        placeholder="Descripción del curso"
                                        value={descripcion}
                                        onChange={e =>
                                            setDescripcion(e.target.value)
                                        }
                                        required
                                    />
                                </div>

                                <div className="col-md-4 mb-3">
                                    <label className="form-label">
                                        Créditos *
                                    </label>
                                    <input
                                        type="text"
                                        inputMode="numeric"
                                        maxLength="1"
                                        className="form-control"
                                        placeholder="Ej: 4"
                                        value={creditos}
                                        onChange={e => {
                                            if (/^\d*$/.test(e.target.value))
                                                setCreditos(e.target.value);
                                        }}
                                        required
                                    />
                                </div>

                                <div className="col-md-4 mb-3">
                                    <label className="form-label">
                                        Ciclo *
                                    </label>
                                    <select
                                        className="form-select"
                                        value={ciclo}
                                        onChange={e =>
                                            setCiclo(e.target.value)
                                        }
                                        required
                                    >
                                        <option value="">
                                            Seleccione un ciclo
                                        </option>
                                        {[
                                            "I", "II", "III", "IV", "V",
                                            "VI", "VII", "VIII", "IX", "X"
                                        ].map(c => (
                                            <option key={c} value={c}>
                                                {c}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="col-md-4 mb-3">
                                    <label className="form-label">
                                        Horas Semanales *
                                    </label>
                                    <input
                                        type="text"
                                        inputMode="numeric"
                                        maxLength="2"
                                        className="form-control"
                                        placeholder="Ej: 6"
                                        value={horas}
                                        onChange={e => {
                                            if (/^\d*$/.test(e.target.value))
                                                setHoras(e.target.value);
                                        }}
                                        required
                                    />
                                </div>

                                <div className="col-md-6 mb-3">
                                    <label className="form-label">
                                        Docente *
                                    </label>
                                    <select
                                        className="form-select"
                                        value={docente}
                                        onChange={e =>
                                            setDocente(e.target.value)
                                        }
                                        required
                                    >
                                        <option value="">
                                            Seleccione un docente
                                        </option>
                                        {docentes.map(d => (
                                            <option
                                                key={d.id_docente}
                                                value={d.id_docente}
                                            >
                                                ID {d.id_docente} - {d.especialidad}
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
                                {editando !== null
                                    ? "Actualizar Curso"
                                    : "Guardar Curso"}
                            </button>
                        </form>
                    </div>
                </div>
            )}

            <div className="card shadow-sm mt-4">
                <div className="card-body">
                    <h4 className="mb-4">
                        Cursos Registrados
                    </h4>

                    {cargando ? (
                        <div className="text-center py-4">
                            <div
                                className="spinner-border text-primary"
                                role="status"
                            />
                            <p className="text-muted mt-2">
                                Cargando cursos...
                            </p>
                        </div>
                    ) : cursos.length === 0 ? (
                        <div className="alert alert-info">
                            No hay cursos registrados.
                        </div>
                    ) : (
                        <div className="table-responsive">
                            <table className="table table-hover align-middle">
                                <thead className="table-light">
                                    <tr>
                                        <th>ID</th>
                                        <th>Nombre</th>
                                        <th>Descripción</th>
                                        <th>Créditos</th>
                                        <th>Ciclo</th>
                                        <th>Horas</th>
                                        <th>Docente</th>
                                        <th>Acciones</th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {cursos.map(curso => (
                                        <tr key={curso.id_curso}>
                                            <td>{curso.id_curso}</td>
                                            <td>
                                                <strong>
                                                    {curso.nombre}
                                                </strong>
                                            </td>
                                            <td>
                                                {curso.descripcion || "—"}
                                            </td>
                                            <td>{curso.creditos}</td>
                                            <td>{curso.ciclo}</td>
                                            <td>{curso.horas_semanales}</td>
                                            <td>
                                                {obtenerDocente(
                                                    curso.id_docente
                                                )}
                                            </td>
                                            <td>
                                                <button
                                                    type="button"
                                                    className="btn btn-warning btn-sm me-2"
                                                    onClick={() =>
                                                        editarCurso(curso)
                                                    }
                                                >
                                                    Editar
                                                </button>

                                                <button
                                                    type="button"
                                                    className="btn btn-danger btn-sm"
                                                    onClick={() =>
                                                        eliminarCurso(
                                                            curso.id_curso
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

export default Cursos;
