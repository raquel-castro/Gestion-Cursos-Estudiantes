
import { useEffect, useState } from "react";
import api from "../../api/axios";
import "./docentes.css";

import {
  alertaExito,
  alertaError,
  alertaAdvertencia,
  confirmarAccion
} from "../../utils/alertas";

const CARRERAS = [
  "ADMINISTRACION",
  "CONTABILIDAD",
  "DESARROLLO DE SISTEMAS DE INFORMACION"
];

const FORMULARIO_VACIO = {
  dni: "",
  id_persona: null,
  nombre: "",
  carrera: "",
  ids_cursos: []
};

function Docentes() {
  const [formulario, setFormulario] = useState(FORMULARIO_VACIO);
  const [docentes, setDocentes] = useState([]);
  const [personas, setPersonas] = useState([]);
  const [cursos, setCursos] = useState([]);
  const [cursosAsignados, setCursosAsignados] = useState({});
  const [busqueda, setBusqueda] = useState({
    dni: "",
    carrera: "",
    nombre: ""
  });

  const [editando, setEditando] = useState(null);
  const [mostrarResultados, setMostrarResultados] = useState(false);
  const [cargando, setCargando] = useState(false);
  const [guardando, setGuardando] = useState(false);
  const [buscandoDni, setBuscandoDni] = useState(false);

  const cargarCatalogos = async () => {
    try {
      const [respuestaPersonas, respuestaCursos] = await Promise.all([
        api.get("/personas/"),
        api.get("/cursos/")
      ]);

      setPersonas(respuestaPersonas.data);
      setCursos(respuestaCursos.data);
    } catch (error) {
      alertaError(
        error.response?.data?.detail ||
        "No se pudieron cargar las personas o los cursos."
      );
    }
  };

  useEffect(() => {
    cargarCatalogos();
  }, []);

  const limpiarFormulario = () => {
    setFormulario({ ...FORMULARIO_VACIO });
    setEditando(null);
  };

  const buscarPersonaPorDni = async () => {
    const dni = formulario.dni.trim();

    if (!/^\d{8}$/.test(dni)) {
      alertaAdvertencia("Ingrese un DNI de 8 dígitos.");
      return;
    }

    try {
      setBuscandoDni(true);

      const respuesta = await api.get("/personas/buscar", {
        params: { dni }
      });

      const persona = respuesta.data[0];

      if (!persona) {
        setFormulario(anterior => ({
          ...anterior,
          id_persona: null,
          nombre: ""
        }));
        alertaAdvertencia("No se encontró una persona con ese DNI.");
        return;
      }

      setFormulario(anterior => ({
        ...anterior,
        id_persona: persona.id_persona,
        nombre: `${persona.apellidos} ${persona.nombres}`
      }));
    } catch (error) {
      alertaError(
        error.response?.data?.detail ||
        "No se pudo buscar el DNI."
      );
    } finally {
      setBuscandoDni(false);
    }
  };

  const cambiarCarrera = (carrera) => {
    setFormulario(anterior => ({
      ...anterior,
      carrera,
      ids_cursos: []
    }));
  };

  const alternarCurso = (idCurso) => {
    setFormulario(anterior => {
      const seleccionado = anterior.ids_cursos.includes(idCurso);

      return {
        ...anterior,
        ids_cursos: seleccionado
          ? anterior.ids_cursos.filter(id => id !== idCurso)
          : [...anterior.ids_cursos, idCurso]
      };
    });
  };

  const cursosDisponibles = cursos.filter(
    curso => curso.carrera === formulario.carrera
  );

  const guardarDocente = async (e) => {
    e.preventDefault();

    if (!formulario.id_persona) {
      alertaAdvertencia("Primero busque un DNI válido.");
      return;
    }

    if (!formulario.carrera) {
      alertaAdvertencia("Seleccione una carrera.");
      return;
    }

    if (formulario.ids_cursos.length === 0) {
      alertaAdvertencia("Seleccione al menos un curso.");
      return;
    }

    try {
      setGuardando(true);

      if (editando !== null) {
        await api.put(`/docentes/${editando}`, {
          especialidad: formulario.carrera,
          id_persona: formulario.id_persona
        });

        await api.put(`/docentes/${editando}/cursos`, {
          ids_cursos: formulario.ids_cursos
        });

        alertaExito("Docente actualizado correctamente.");
      } else {
        await api.post("/docentes/con-cursos", {
          especialidad: formulario.carrera,
          id_persona: formulario.id_persona,
          ids_cursos: formulario.ids_cursos
        });

        alertaExito("Docente y cursos registrados correctamente.");
      }

      limpiarFormulario();

      if (mostrarResultados) {
        await consultarDocentes();
      }
    } catch (error) {
      alertaError(
        error.response?.data?.detail ||
        "No se pudo guardar el docente."
      );
    } finally {
      setGuardando(false);
    }
  };

  const cargarCursosDeDocentes = async (lista) => {
    const resultados = await Promise.all(
      lista.map(async docente => {
        try {
          const respuesta = await api.get(
            `/docentes/${docente.id_docente}/cursos`
          );

          return [docente.id_docente, respuesta.data];
        } catch {
          return [docente.id_docente, []];
        }
      })
    );

    setCursosAsignados(Object.fromEntries(resultados));
  };

  const consultarDocentes = async (e) => {
    if (e) e.preventDefault();

    try {
      setCargando(true);

      const respuesta = await api.get("/docentes/");
      let lista = respuesta.data;

      if (busqueda.carrera) {
        lista = lista.filter(
          docente => docente.especialidad === busqueda.carrera
        );
      }

      if (busqueda.dni.trim()) {
        lista = lista.filter(docente => {
          const persona = personas.find(
            p => p.id_persona === docente.id_persona
          );
          return persona?.dni.includes(busqueda.dni.trim());
        });
      }

      if (busqueda.nombre.trim()) {
        const texto = busqueda.nombre.toLowerCase();

        lista = lista.filter(docente => {
          const persona = personas.find(
            p => p.id_persona === docente.id_persona
          );

          return `${persona?.apellidos || ""} ${persona?.nombres || ""}`
            .toLowerCase()
            .includes(texto);
        });
      }

      setDocentes(lista);
      await cargarCursosDeDocentes(lista);
      setMostrarResultados(true);
    } catch (error) {
      alertaError(
        error.response?.data?.detail ||
        "No se pudieron consultar los docentes."
      );
    } finally {
      setCargando(false);
    }
  };

  const editarDocente = async (docente) => {
    const persona = personas.find(
      p => p.id_persona === docente.id_persona
    );

    try {
      const respuesta = await api.get(
        `/docentes/${docente.id_docente}/cursos`
      );

      setFormulario({
        dni: persona?.dni || "",
        id_persona: docente.id_persona,
        nombre: persona
          ? `${persona.apellidos} ${persona.nombres}`
          : "",
        carrera: docente.especialidad,
        ids_cursos: respuesta.data.map(c => c.id_curso)
      });

      setEditando(docente.id_docente);
      window.scrollTo({ top: 0, behavior: "smooth" });
    } catch {
      alertaError("No se pudieron cargar los cursos del docente.");
    }
  };

  const eliminarDocente = async (docente) => {
    const confirmado = await confirmarAccion(
      "¿Está seguro de eliminar este docente?"
    );

    if (!confirmado) return;

    try {
      await api.delete(`/docentes/${docente.id_docente}`);
      alertaExito("Docente eliminado correctamente.");
      await consultarDocentes();
    } catch (error) {
      alertaError(
        error.response?.data?.detail ||
        "No se pudo eliminar el docente."
      );
    }
  };

  const obtenerPersona = (idPersona) =>
    personas.find(p => p.id_persona === idPersona);

  return (
    <div className="docentes-page container-fluid px-3 px-md-4 mt-4">
      <h1 className="mb-4">Registro de Docentes</h1>

      {/* REGISTRO */}
      <div className="card shadow-sm mb-4">
        <div className="card-header bg-primary text-white">
          <h5 className="mb-0">
            {editando !== null
              ? "Editar docente"
              : "Registrar nuevo docente"}
          </h5>
        </div>

        <div className="card-body">
          <form onSubmit={guardarDocente}>
            <div className="row g-3">
              <div className="col-md-4">
                <label className="form-label">
                  DNI <span className="text-danger">*</span>
                </label>

                <div className="input-group">
                  <input
                    className="form-control"
                    value={formulario.dni}
                    maxLength={8}
                    placeholder="Ingrese DNI"
                    onChange={e =>
                      setFormulario(anterior => ({
                        ...anterior,
                        dni: e.target.value.replace(/\D/g, ""),
                        id_persona: null,
                        nombre: ""
                      }))
                    }
                    required
                  />

                  <button
                    type="button"
                    className="btn btn-outline-primary"
                    onClick={buscarPersonaPorDni}
                    disabled={buscandoDni}
                  >
                    {buscandoDni ? "Buscando..." : "Buscar"}
                  </button>
                </div>
              </div>

              <div className="col-md-8">
                <label className="form-label">
                  Apellidos y nombres
                </label>
                <input
                  className="form-control"
                  value={formulario.nombre}
                  placeholder="Se completará al buscar el DNI"
                  readOnly
                />
              </div>

              <div className="col-md-6">
                <label className="form-label">
                  Carrera <span className="text-danger">*</span>
                </label>

                <select
                  className="form-select"
                  value={formulario.carrera}
                  onChange={e => cambiarCarrera(e.target.value)}
                  required
                >
                  <option value="">Seleccione una carrera</option>

                  {CARRERAS.map(carrera => (
                    <option key={carrera} value={carrera}>
                      {carrera}
                    </option>
                  ))}
                </select>
              </div>

              <div className="col-12">
                <label className="form-label">
                  Cursos que dictará el docente
                  <span className="text-danger"> *</span>
                </label>

                {!formulario.carrera ? (
                  <div className="alert alert-info mb-0">
                    Seleccione una carrera para mostrar sus cursos.
                  </div>
                ) : cursosDisponibles.length === 0 ? (
                  <div className="alert alert-warning mb-0">
                    No hay cursos disponibles para esta carrera.
                  </div>
                ) : (
                  <div
                    className="border rounded p-3"
                    style={{ maxHeight: 300, overflowY: "auto" }}
                  >
                    <div className="row">
                      {cursosDisponibles.map(curso => (
                        <div
                          className="col-md-6 mb-2"
                          key={curso.id_curso}
                        >
                          <label className="d-flex gap-2 align-items-start">
                            <input
                              type="checkbox"
                              className="form-check-input mt-1"
                              checked={formulario.ids_cursos.includes(
                                curso.id_curso
                              )}
                              onChange={() =>
                                alternarCurso(curso.id_curso)
                              }
                            />

                            <span>
                              <strong>{curso.nombre}</strong>
                              <br />
                              <small className="text-muted">
                                Semestre {curso.ciclo} ·
                                {" "}{curso.creditos} créditos ·
                                {" "}{curso.horas_semanales ?? "—"} h/sem.
                              </small>
                            </span>
                          </label>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {formulario.carrera && (
                  <small className="text-muted">
                    {formulario.ids_cursos.length} curso(s) seleccionado(s)
                  </small>
                )}
              </div>
            </div>

            <div className="mt-4 d-flex gap-2">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={guardando}
              >
                {guardando
                  ? "Guardando..."
                  : editando !== null
                    ? "ACTUALIZAR DOCENTE"
                    : "GRABAR DOCENTE"}
              </button>

              <button
                type="button"
                className="btn btn-secondary"
                onClick={limpiarFormulario}
              >
                Limpiar
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* CONSULTA */}
      <div className="card shadow-sm mb-4">
        <div className="card-header bg-primary text-white">
          <h5 className="mb-0">Consultar Docentes</h5>
        </div>

        <div className="card-body">
          <form onSubmit={consultarDocentes}>
            <div className="row g-3">
              <div className="col-md-4">
                <label className="form-label">DNI</label>
                <input
                  className="form-control"
                  maxLength={8}
                  value={busqueda.dni}
                  onChange={e =>
                    setBusqueda(anterior => ({
                      ...anterior,
                      dni: e.target.value.replace(/\D/g, "")
                    }))
                  }
                  placeholder="Buscar por DNI"
                />
              </div>

              <div className="col-md-4">
                <label className="form-label">Docente</label>
                <input
                  className="form-control"
                  value={busqueda.nombre}
                  onChange={e =>
                    setBusqueda(anterior => ({
                      ...anterior,
                      nombre: e.target.value
                    }))
                  }
                  placeholder="Apellidos o nombres"
                />
              </div>

              <div className="col-md-4">
                <label className="form-label">Carrera</label>
                <select
                  className="form-select"
                  value={busqueda.carrera}
                  onChange={e =>
                    setBusqueda(anterior => ({
                      ...anterior,
                      carrera: e.target.value
                    }))
                  }
                >
                  <option value="">Todas las carreras</option>
                  {CARRERAS.map(carrera => (
                    <option key={carrera} value={carrera}>
                      {carrera}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="mt-3 d-flex gap-2">
              <button
                type="submit"
                className="btn btn-primary"
                disabled={cargando}
              >
                Buscar
              </button>

              <button
                type="button"
                className="btn btn-secondary"
                onClick={() => {
                  setBusqueda({ dni: "", nombre: "", carrera: "" });
                  setMostrarResultados(false);
                  setDocentes([]);
                }}
              >
                Limpiar
              </button>
            </div>
          </form>
        </div>
      </div>

      {/* RESULTADOS SOLO DESPUÉS DE BUSCAR */}
      {mostrarResultados && (
        <div className="card shadow-sm mb-4">
          <div className="card-body">
            <h5 className="mb-3">
              Resultados de búsqueda ({docentes.length})
            </h5>

            {cargando ? (
              <p>Buscando docentes...</p>
            ) : docentes.length === 0 ? (
              <div className="alert alert-info">
                No se encontraron docentes.
              </div>
            ) : (
              <div className="table-responsive">
                <table className="table table-hover align-middle">
                  <thead className="table-light">
                    <tr>
                      <th>DNI</th>
                      <th>Apellidos y nombres</th>
                      <th>Carrera</th>
                      <th>Cursos asignados</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>

                  <tbody>
                    {docentes.map(docente => {
                      const persona = obtenerPersona(
                        docente.id_persona
                      );

                      const asignados =
                        cursosAsignados[docente.id_docente] || [];

                      return (
                        <tr key={docente.id_docente}>
                          <td>{persona?.dni || "—"}</td>

                          <td>
                            {persona
                              ? `${persona.apellidos} ${persona.nombres}`
                              : "—"}
                          </td>

                          <td>{docente.especialidad}</td>

                          <td>
                            {asignados.length === 0
                              ? "Sin cursos"
                              : asignados.map(curso => (
                                  <div key={curso.id_curso}>
                                    {curso.nombre}
                                    <small className="text-muted">
                                      {" "}({curso.ciclo},
                                      {" "}{curso.creditos} créditos,
                                      {" "}{curso.horas_semanales ?? "—"} h)
                                    </small>
                                  </div>
                                ))}
                          </td>

                          <td>
                            <div className="d-flex gap-2">
                              <button
                                type="button"
                                className="btn btn-warning btn-sm"
                                onClick={() => editarDocente(docente)}
                              >
                                Editar
                              </button>

                              <button
                                type="button"
                                className="btn btn-danger btn-sm"
                                onClick={() => eliminarDocente(docente)}
                              >
                                Eliminar
                              </button>
                            </div>
                          </td>
                        </tr>
                      );
                    })}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default Docentes;
