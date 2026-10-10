import { useEffect, useState } from "react";
import api from "../../api/axios";
import Busqueda from "../../components/busqueda/Busqueda";
import "../../components/busqueda/busqueda.css";
import "./matriculas.css";

import {
    alertaExito,
    alertaError,
    alertaAdvertencia,
    confirmarAccion
} from "../../utils/alertas";

const API_MATRICULAS = "/matriculas/";
const API_ALUMNOS = "/alumnos/";
const API_CURSOS = "/cursos/";

function Matriculas() {
    const [matriculas, setMatriculas] = useState([]);
    const [alumnos, setAlumnos] = useState([]);
    const [cursos, setCursos] = useState([]);
    const [mostrarFormulario, setMostrarFormulario] = useState(false);

    const [fechaMatricula, setFechaMatricula] = useState("");
    const [estado, setEstado] = useState("ACTIVO");
    const [alumno, setAlumno] = useState("");
    const [curso, setCurso] = useState("");

    const [editando, setEditando] = useState(null);
    const [cargando, setCargando] = useState(true);
    const [busqueda, setBusqueda] = useState({ id: "", id_alumno: "", id_curso: "", estado: "" });

    const cargarDatos = async () => {
        try {
            setCargando(true);

            const [
                respuestaMatriculas,
                respuestaAlumnos,
                respuestaCursos
            ] = await Promise.all([
                api.get(API_MATRICULAS),
                api.get(API_ALUMNOS),
                api.get(API_CURSOS)
            ]);

            setMatriculas(respuestaMatriculas.data);
            setAlumnos(respuestaAlumnos.data);
            setCursos(respuestaCursos.data);

        } catch (error) {
            console.error(
                "Error al cargar matrículas:",
                error
            );

            alertaError(
                error.response?.data?.detail ||
                "No se pudieron cargar las matrículas."
            );
        } finally {
            setCargando(false);
        }
    };

    useEffect(() => {
        cargarDatos();
    }, []);

    const buscarMatriculas = async (e) => {
        e.preventDefault();
        const params = {};
        if (busqueda.id) params.id = Number(busqueda.id);
        if (busqueda.id_alumno) params.id_alumno = Number(busqueda.id_alumno);
        if (busqueda.id_curso) params.id_curso = Number(busqueda.id_curso);
        if (busqueda.estado) params.estado = busqueda.estado;
        if (Object.keys(params).length === 0) {
            await cargarDatos();
            return;
        }
        try {
            setCargando(true);
            const respuesta = await api.get(`${API_MATRICULAS}buscar`, { params });
            setMatriculas(respuesta.data);
        } catch (error) {
            alertaError(error.response?.data?.detail || "No se pudieron buscar las matrículas.");
        } finally {
            setCargando(false);
        }
    };

    const limpiarBusqueda = async () => {
        setBusqueda({ id: "", id_alumno: "", id_curso: "", estado: "" });
        await cargarDatos();
    };

    const limpiarFormulario = () => {
        setFechaMatricula("");
        setEstado("ACTIVO");
        setAlumno("");
        setCurso("");
        setEditando(null);
    };

    const cambiarFormulario = () => {
        if (mostrarFormulario) {
            limpiarFormulario();
        }

        setMostrarFormulario(!mostrarFormulario);
    };

    const guardarMatricula = async (e) => {
        e.preventDefault();

        if (fechaMatricula === "") {
            alertaAdvertencia(
                "La fecha de matrícula es obligatoria."
            );
            return;
        }

        if (alumno === "") {
            alertaAdvertencia(
                "Debe seleccionar un alumno."
            );
            return;
        }

        if (curso === "") {
            alertaAdvertencia(
                "Debe seleccionar un curso."
            );
            return;
        }

        const datos = {
            fecha_matricula: fechaMatricula,
            estado,
            id_alumno: Number(alumno),
            id_curso: Number(curso)
        };

        try {
            if (editando !== null) {
                await api.put(
                    `${API_MATRICULAS}${editando}`,
                    datos
                );

                alertaExito(
                    "Matrícula actualizada correctamente."
                );
            } else {
                await api.post(
                    API_MATRICULAS,
                    datos
                );

                alertaExito(
                    "Matrícula registrada correctamente."
                );
            }

            limpiarFormulario();
            setMostrarFormulario(false);
            await cargarDatos();

        } catch (error) {
            console.error(
                "Error al guardar matrícula:",
                error
            );

            alertaError(
                error.response?.data?.detail ||
                "No se pudo guardar la matrícula."
            );
        }
    };

    const editarMatricula = (matricula) => {
        setFechaMatricula(
            String(matricula.fecha_matricula).substring(0, 10)
        );

        setEstado(matricula.estado);
        setAlumno(String(matricula.id_alumno));
        setCurso(String(matricula.id_curso));
        setEditando(matricula.id_matricula);
        setMostrarFormulario(true);

        window.scrollTo({
            top: 0,
            behavior: "smooth"
        });
    };

    const eliminarMatricula = async (id) => {
        const confirmado = await confirmarAccion(
            `¿Está seguro de eliminar la matrícula ID=${id}?`
        );

        if (!confirmado) return;

        try {
            await api.delete(
                `${API_MATRICULAS}${id}`
            );

            alertaExito(
                "Matrícula eliminada correctamente."
            );

            await cargarDatos();

        } catch (error) {
            console.error(
                "Error al eliminar matrícula:",
                error
            );

            alertaError(
                error.response?.data?.detail ||
                "No se pudo eliminar la matrícula."
            );
        }
    };

    const obtenerAlumno = (id) => {
        const alumnoEncontrado = alumnos.find(
            (a) => a.id_alumno === id
        );

        if (!alumnoEncontrado) {
            return `ID ${id}`;
        }

        return `ID ${alumnoEncontrado.id_alumno} - ${alumnoEncontrado.codigo_alumno}`;
    };

    const obtenerCurso = (id) => {
        const cursoEncontrado = cursos.find(
            (c) => c.id_curso === id
        );

        if (!cursoEncontrado) {
            return `ID ${id}`;
        }

        return `ID ${cursoEncontrado.id_curso} - ${cursoEncontrado.nombre}`;
    };

    return (
        <div className="matriculas-page container-fluid px-3 px-md-4 mt-4">

            <div className="d-flex justify-content-between align-items-center mb-4">
                <div>
                    <h1 className="mb-1">
                        Registro de Matrícula
                    </h1>

                    <p className="text-muted mb-0">
                        Gestión de matrículas registradas
                    </p>
                </div>

                <span className="page-count-badge">
                    {matriculas.length}
                </span>
            </div>

            <div className="d-flex justify-content-end mb-4">
                <button
                    type="button"
                    className="btn btn-primary"
                    onClick={cambiarFormulario}
                >
                    {mostrarFormulario
                        ? "− Ocultar registro"
                        : "＋ Registrar matrícula"}
                </button>
            </div>

            {mostrarFormulario && (
                <div className="card shadow-sm">
                    <div className="card-body">

                        <h4 className="mb-4">
                            {editando !== null
                                ? "Editar Matrícula"
                                : "Información de la Matrícula"}
                        </h4>

                        <form onSubmit={guardarMatricula}>
                            <div className="row">

                                <div className="col-md-4 mb-3">
                                    <label className="form-label">
                                        Fecha de Matrícula{" "}
                                        <span className="text-danger">
                                            *
                                        </span>
                                    </label>

                                    <input
                                        type="date"
                                        className="form-control"
                                        value={fechaMatricula}
                                        onChange={(e) =>
                                            setFechaMatricula(
                                                e.target.value
                                            )
                                        }
                                        required
                                    />
                                </div>

                                <div className="col-md-4 mb-3">
                                    <label className="form-label">
                                        Estado{" "}
                                        <span className="text-danger">
                                            *
                                        </span>
                                    </label>

                                    <select
                                        className="form-select"
                                        value={estado}
                                        onChange={(e) =>
                                            setEstado(e.target.value)
                                        }
                                        required
                                    >
                                        <option value="ACTIVO">
                                            Activo
                                        </option>

                                        <option value="RETIRADO">
                                            Retirado
                                        </option>

                                        <option value="FINALIZADO">
                                            Finalizado
                                        </option>
                                    </select>
                                </div>

                                <div className="col-md-6 mb-3">
                                    <label className="form-label">
                                        Alumno{" "}
                                        <span className="text-danger">
                                            *
                                        </span>
                                    </label>

                                    <select
                                        className="form-select"
                                        value={alumno}
                                        onChange={(e) =>
                                            setAlumno(e.target.value)
                                        }
                                        required
                                    >
                                        <option value="">
                                            Seleccione un alumno
                                        </option>

                                        {alumnos.map((a) => (
                                            <option
                                                key={a.id_alumno}
                                                value={a.id_alumno}
                                            >
                                                {a.codigo_alumno}
                                                {" - ID "}
                                                {a.id_alumno}
                                            </option>
                                        ))}
                                    </select>
                                </div>

                                <div className="col-md-6 mb-3">
                                    <label className="form-label">
                                        Curso{" "}
                                        <span className="text-danger">
                                            *
                                        </span>
                                    </label>

                                    <select
                                        className="form-select"
                                        value={curso}
                                        onChange={(e) =>
                                            setCurso(e.target.value)
                                        }
                                        required
                                    >
                                        <option value="">
                                            Seleccione un curso
                                        </option>

                                        {cursos.map((c) => (
                                            <option
                                                key={c.id_curso}
                                                value={c.id_curso}
                                            >
                                                {c.nombre}
                                                {" - Ciclo "}
                                                {c.ciclo}
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
                                        ? "Actualizar Matrícula"
                                        : "Guardar Matrícula"}
                                </button>
                            </div>
                        </form>

                    </div>
                </div>
            )}

            <Busqueda
                campos={[
                    { name: "id", label: "ID", type: "number", placeholder: "Ej: 1", value: busqueda.id, onChange: (e) => setBusqueda({ ...busqueda, id: e.target.value }) },
                    { name: "id_alumno", label: "Alumno", type: "select", value: busqueda.id_alumno, onChange: (e) => setBusqueda({ ...busqueda, id_alumno: e.target.value }), options: [{ value: "", label: "Todos los alumnos" }, ...alumnos.map((a) => ({ value: String(a.id_alumno), label: `${a.codigo_alumno}` }))] },
                    { name: "id_curso", label: "Curso", type: "select", value: busqueda.id_curso, onChange: (e) => setBusqueda({ ...busqueda, id_curso: e.target.value }), options: [{ value: "", label: "Todos los cursos" }, ...cursos.map((c) => ({ value: String(c.id_curso), label: c.nombre }))] },
                    { name: "estado", label: "Estado", type: "select", value: busqueda.estado, onChange: (e) => setBusqueda({ ...busqueda, estado: e.target.value }), options: [{ value: "", label: "Todos los estados" }, { value: "ACTIVO", label: "ACTIVO" }, { value: "RETIRADO", label: "RETIRADO" }, { value: "FINALIZADO", label: "FINALIZADO" }] }
                ]}
                onBuscar={buscarMatriculas}
                onLimpiar={limpiarBusqueda}
                cargando={cargando}
            />

            <div className="card shadow-sm mt-4">
                <div className="card-body">

                    <h4 className="mb-4">
                        Matrículas Registradas
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
                                Cargando matrículas...
                            </p>
                        </div>
                    )}

                    {!cargando && matriculas.length === 0 && (
                        <div className="alert alert-info">
                            No hay matrículas registradas.
                        </div>
                    )}

                    {!cargando && matriculas.length > 0 && (
                        <div className="table-responsive">
                            <table className="table table-hover align-middle">

                                <thead className="table-light">
                                    <tr>
                                        <th>ID</th>
                                        <th>Fecha</th>
                                        <th>Estado</th>
                                        <th>Alumno</th>
                                        <th>Curso</th>
                                        <th className="text-center">
                                            Acciones
                                        </th>
                                    </tr>
                                </thead>

                                <tbody>
                                    {matriculas.map((matricula) => (
                                        <tr
                                            key={
                                                matricula.id_matricula
                                            }
                                        >
                                            <td>
                                                {matricula.id_matricula}
                                            </td>

                                            <td>
                                                {String(
                                                    matricula.fecha_matricula
                                                ).substring(0, 10)}
                                            </td>

                                            <td>
                                                <span
                                                    className={
                                                        matricula.estado === "ACTIVO"
                                                            ? "badge bg-success"
                                                            : matricula.estado === "RETIRADO"
                                                            ? "badge bg-danger"
                                                            : "badge bg-secondary"
                                                    }
                                                >
                                                    {matricula.estado}
                                                </span>
                                            </td>

                                            <td>
                                                {obtenerAlumno(
                                                    matricula.id_alumno
                                                )}
                                            </td>

                                            <td>
                                                {obtenerCurso(
                                                    matricula.id_curso
                                                )}
                                            </td>

                                            <td className="text-center">
                                                <button
                                                    type="button"
                                                    className="btn btn-warning btn-sm me-2"
                                                    onClick={() =>
                                                        editarMatricula(
                                                            matricula
                                                        )
                                                    }
                                                >
                                                    Editar
                                                </button>

                                                <button
                                                    type="button"
                                                    className="btn btn-danger btn-sm"
                                                    onClick={() =>
                                                        eliminarMatricula(
                                                            matricula.id_matricula
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

export default Matriculas;
