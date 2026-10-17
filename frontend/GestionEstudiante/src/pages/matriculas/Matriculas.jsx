
import { useEffect, useMemo, useState } from "react";
import api from "../../api/axios";
import "./matriculas.css";

import {
  alertaExito,
  alertaError,
  alertaAdvertencia
} from "../../utils/alertas";

const API_MATRICULAS = "/matriculas/";
const API_ALUMNOS = "/alumnos/";

const FORMULARIO_VACIO = {
  dni: "",
  ciclo: "",
  periodo_academico: "",
  condicion: ""
};

const FILTROS_VACIOS = {
  dni: "",
  nombre: ""
};

const CARRERAS = [
  {
    valor: "ADMINISTRACION",
    texto: "ADMINISTRACIÓN"
  },
  {
    valor: "CONTABILIDAD",
    texto: "CONTABILIDAD"
  },
  {
    valor: "DESARROLLO DE SISTEMAS DE INFORMACION",
    texto: "DESARROLLO DE SISTEMAS DE INFORMACIÓN"
  }
];

const CICLOS = ["I", "II", "III", "IV", "V", "VI"];
const CONDICIONES = ["NUEVO", "REGULAR", "REINGRESO"];

function obtenerError(error, mensaje) {
  const detalle = error?.response?.data?.detail;

  if (typeof detalle === "string") return detalle;

  if (Array.isArray(detalle)) {
    return detalle
      .map(item => item.msg || "Dato inválido")
      .join(". ");
  }

  return mensaje;
}

function mostrarValor(valor) {
  return valor || "—";
}

function mostrarCarrera(valor) {
  if (!valor) return "—";

  return (
    CARRERAS.find(c => c.valor === valor)?.texto ||
    valor
  );
}

export default function Matriculas() {
  const [matriculas, setMatriculas] = useState([]);
  const [alumnos, setAlumnos] = useState([]);
  const [personas, setPersonas] = useState([]);

  const [formulario, setFormulario] = useState({
    ...FORMULARIO_VACIO
  });

  const [alumnoSeleccionado, setAlumnoSeleccionado] =
    useState(null);

  const [personaSeleccionada, setPersonaSeleccionada] =
    useState(null);

  const [filtros, setFiltros] = useState({
    ...FILTROS_VACIOS
  });

  const [filtrosAplicados, setFiltrosAplicados] = useState({
    ...FILTROS_VACIOS
  });

  // Los resultados permanecen ocultos hasta buscar.
  const [consultado, setConsultado] = useState(false);

  const [editando, setEditando] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [buscando, setBuscando] = useState(false);
  const [guardando, setGuardando] = useState(false);

  // ==========================================
  // CARGAR DATOS
  // ==========================================

  const cargarDatos = async () => {
    try {
      setCargando(true);

      const [
        respuestaMatriculas,
        respuestaAlumnos,
        respuestaPersonas
      ] = await Promise.all([
        api.get(API_MATRICULAS),
        api.get(API_ALUMNOS),
        api.get("/personas/")
      ]);

      setMatriculas(respuestaMatriculas.data);
      setAlumnos(respuestaAlumnos.data);
      setPersonas(respuestaPersonas.data);

    } catch (error) {
      console.error(error);

      alertaError(
        obtenerError(
          error,
          "No se pudieron cargar las matrículas."
        )
      );

    } finally {
      setCargando(false);
    }
  };

  useEffect(() => {
    cargarDatos();
  }, []);

  // ==========================================
  // DATOS DE ALUMNOS Y PERSONAS
  // ==========================================

  const obtenerPersona = alumno => {
    if (!alumno) return null;

    return personas.find(
      persona =>
        Number(persona.id_persona) ===
        Number(alumno.id_persona)
    ) || null;
  };

  const obtenerAlumnoPorId = id => {
    return alumnos.find(
      alumno =>
        Number(alumno.id_alumno) === Number(id)
    );
  };

  const obtenerDni = alumno => {
    if (!alumno) return "";

    const persona = obtenerPersona(alumno);

    return String(
      alumno.dni || persona?.dni || ""
    );
  };

  const obtenerNombre = alumno => {
    if (!alumno) return "";

    const persona = obtenerPersona(alumno);

    if (persona) {
      return [
        persona.apellidos,
        persona.nombres
      ].filter(Boolean).join(" ");
    }

    return alumno.nombre_completo || "";
  };

  // ==========================================
  // BUSCAR ALUMNO POR DNI
  // ==========================================

  const buscarAlumno = async () => {
    const dni = formulario.dni.trim();

    if (!/^\d{8}$/.test(dni)) {
      alertaAdvertencia(
        "El DNI debe tener exactamente 8 dígitos."
      );
      return;
    }

    try {
      setBuscando(true);

      const respuesta = await api.get(
        `${API_ALUMNOS}persona/${dni}`
      );

      const persona = respuesta.data;

      const alumno = alumnos.find(item => {
        const personaAlumno = obtenerPersona(item);

        return (
          String(
            item.dni || personaAlumno?.dni || ""
          ) === dni
        );
      });

      if (!alumno) {
        setAlumnoSeleccionado(null);
        setPersonaSeleccionada(null);

        alertaAdvertencia(
          "La persona existe, pero todavía no está registrada como alumno."
        );
        return;
      }

      if (!alumno.carrera || !alumno.turno_actual) {
        setAlumnoSeleccionado(null);
        setPersonaSeleccionada(null);

        alertaAdvertencia(
          "El alumno debe tener carrera y turno registrados."
        );
        return;
      }

      setAlumnoSeleccionado(alumno);
      setPersonaSeleccionada(persona);

    } catch (error) {
      setAlumnoSeleccionado(null);
      setPersonaSeleccionada(null);

      alertaError(
        obtenerError(
          error,
          "No se encontró una persona con ese DNI."
        )
      );

    } finally {
      setBuscando(false);
    }
  };

  // ==========================================
  // FORMULARIO
  // ==========================================

  const cambiarDni = valor => {
    const dni = valor.replace(/\D/g, "").slice(0, 8);

    setFormulario(prev => ({
      ...prev,
      dni
    }));

    setAlumnoSeleccionado(null);
    setPersonaSeleccionada(null);
  };

  const cambiarCampo = (campo, valor) => {
    setFormulario(prev => ({
      ...prev,
      [campo]: valor
    }));
  };

  const limpiarFormulario = () => {
    setFormulario({ ...FORMULARIO_VACIO });
    setAlumnoSeleccionado(null);
    setPersonaSeleccionada(null);
    setEditando(null);
  };

  // ==========================================
  // GUARDAR MATRÍCULA
  // ==========================================

  const guardarMatricula = async evento => {
    evento.preventDefault();

    if (editando === null && !alumnoSeleccionado) {
      alertaAdvertencia(
        "Primero debe buscar un alumno por DNI."
      );
      return;
    }

    if (
      !formulario.ciclo ||
      !formulario.periodo_academico ||
      !formulario.condicion
    ) {
      alertaAdvertencia(
        "Complete el ciclo, periodo académico y condición."
      );
      return;
    }

    if (
      !/^\d{4}-(I|II)$/.test(
        formulario.periodo_academico
      )
    ) {
      alertaAdvertencia(
        "El periodo debe tener el formato 2026-I o 2026-II."
      );
      return;
    }

    const datos = {
      ciclo: formulario.ciclo,
      periodo_academico:
        formulario.periodo_academico,
      condicion: formulario.condicion
    };

    try {
      setGuardando(true);

      if (editando !== null) {
        await api.put(
          `${API_MATRICULAS}${editando}`,
          datos
        );

        alertaExito(
          "Matrícula actualizada correctamente."
        );

      } else {
        await api.post(API_MATRICULAS, {
          id_alumno: alumnoSeleccionado.id_alumno,
          ...datos
        });

        alertaExito(
          "Matrícula registrada correctamente."
        );
      }

      limpiarFormulario();

      await cargarDatos();

      // Se conserva el estado de la consulta.
      // Si no se buscó, los resultados siguen ocultos.

    } catch (error) {
      alertaError(
        obtenerError(
          error,
          "No se pudo guardar la matrícula."
        )
      );

    } finally {
      setGuardando(false);
    }
  };

  // ==========================================
  // EDITAR MATRÍCULA
  // ==========================================

  const editarMatricula = matricula => {
    if (!matricula.periodo_academico) {
      alertaAdvertencia(
        "Este registro es histórico y no se puede editar desde el nuevo formulario."
      );
      return;
    }

    const alumno = obtenerAlumnoPorId(
      matricula.id_alumno
    );

    const persona = obtenerPersona(alumno);

    setAlumnoSeleccionado(alumno || null);
    setPersonaSeleccionada(persona || null);

    setFormulario({
      dni: obtenerDni(alumno),
      ciclo: matricula.ciclo || "",
      periodo_academico:
        matricula.periodo_academico || "",
      condicion: matricula.condicion || ""
    });

    setEditando(matricula.id_matricula);

    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  };

  // ==========================================
  // FILTROS: SOLO DNI Y NOMBRE/APELLIDO
  // ==========================================

  const matriculasFiltradas = useMemo(() => {
    if (!consultado) return [];

    const dniBuscado = filtrosAplicados.dni.trim();

    const nombreBuscado =
      filtrosAplicados.nombre.trim().toLowerCase();

    return matriculas.filter(matricula => {
      const alumno = obtenerAlumnoPorId(
        matricula.id_alumno
      );

      const dni = obtenerDni(alumno);
      const nombre = obtenerNombre(alumno).toLowerCase();

      return (
        dni.includes(dniBuscado) &&
        nombre.includes(nombreBuscado)
      );
    });

  }, [
    consultado,
    matriculas,
    alumnos,
    personas,
    filtrosAplicados
  ]);

  const buscarMatriculas = evento => {
    evento.preventDefault();

    setFiltrosAplicados({ ...filtros });
    setConsultado(true);
  };

  const limpiarFiltros = () => {
    setFiltros({ ...FILTROS_VACIOS });
    setFiltrosAplicados({ ...FILTROS_VACIOS });
    setConsultado(false);
  };

  const nombreSeleccionado = personaSeleccionada
    ? [
        personaSeleccionada.apellidos,
        personaSeleccionada.nombres
      ].filter(Boolean).join(" ")
    : obtenerNombre(alumnoSeleccionado);

  // ==========================================
  // INTERFAZ
  // ==========================================

  return (
    <div className="matriculas-page container-fluid px-3 px-md-4 mt-4">

      {/* ENCABEZADO */}
      <div className="mb-4">
        <h1 className="mb-1">
          Registro de Matrículas
        </h1>

        <p className="text-muted mb-0">
          Gestión de matrículas por periodo académico
        </p>
      </div>

      {/* ====================================
          REGISTRAR MATRÍCULA
          SIEMPRE VISIBLE
      ==================================== */}

      <div className="card shadow-sm mb-4">

        <div
          className="card-header fw-bold"
          style={{
            backgroundColor: "#e1f0ff",
            color: "#123f7a",
            fontSize: "1.2rem",
            padding: "15px 20px"
          }}
        >
          <i className="bi bi-journal-plus me-2" />

          {editando !== null
            ? "Editar Matrícula"
            : "Registrar Matrícula"}
        </div>

        <div className="card-body p-4">

          <form onSubmit={guardarMatricula}>

            {/* DNI Y NOMBRE */}
            <div className="row g-3 mb-3">

              <div className="col-lg-4">
                <label className="form-label">
                  DNI del estudiante{" "}
                  <span className="text-danger">*</span>
                </label>

                <div className="input-group">

                  <input
                    type="text"
                    className="form-control"
                    placeholder="8 dígitos"
                    inputMode="numeric"
                    maxLength={8}
                    value={formulario.dni}
                    disabled={editando !== null}
                    onChange={e =>
                      cambiarDni(e.target.value)
                    }
                    required
                  />

                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={buscarAlumno}
                    disabled={
                      buscando || editando !== null
                    }
                  >
                    <i className="bi bi-search me-1" />
                    {buscando
                      ? "Buscando..."
                      : "Buscar"}
                  </button>

                </div>
              </div>

              <div className="col-lg-8">
                <label className="form-label">
                  Apellidos y nombres
                </label>

                <input
                  type="text"
                  className="form-control"
                  value={nombreSeleccionado}
                  readOnly
                  placeholder="Se completa al buscar el DNI"
                  style={{
                    backgroundColor: "#e9ecef"
                  }}
                />
              </div>
            </div>

            {/* CARRERA Y TURNO */}
            <div className="row g-3 mb-3">

              <div className="col-md-6">
                <label className="form-label">
                  Carrera
                </label>

                <input
                  type="text"
                  className="form-control"
                  value={
                    alumnoSeleccionado
                      ? mostrarCarrera(
                          alumnoSeleccionado.carrera
                        )
                      : ""
                  }
                  readOnly
                  style={{
                    backgroundColor: "#e9ecef"
                  }}
                />
              </div>

              <div className="col-md-6">
                <label className="form-label">
                  Turno
                </label>

                <input
                  type="text"
                  className="form-control"
                  value={
                    alumnoSeleccionado?.turno_actual || ""
                  }
                  readOnly
                  style={{
                    backgroundColor: "#e9ecef"
                  }}
                />
              </div>
            </div>

            {/* DATOS ACADÉMICOS */}
            <div className="row g-3 mb-4">

              <div className="col-md-4">
                <label className="form-label">
                  Ciclo{" "}
                  <span className="text-danger">*</span>
                </label>

                <select
                  className="form-select"
                  value={formulario.ciclo}
                  onChange={e =>
                    cambiarCampo(
                      "ciclo",
                      e.target.value
                    )
                  }
                  required
                >
                  <option value="">
                    Seleccione un ciclo
                  </option>

                  {CICLOS.map(ciclo => (
                    <option
                      key={ciclo}
                      value={ciclo}
                    >
                      {ciclo}
                    </option>
                  ))}
                </select>
              </div>

              <div className="col-md-4">
                <label className="form-label">
                  Periodo académico{" "}
                  <span className="text-danger">*</span>
                </label>

                <input
                  type="text"
                  className="form-control"
                  placeholder="Ej: 2026-II"
                  maxLength={7}
                  pattern="[0-9]{4}-(I|II)"
                  value={formulario.periodo_academico}
                  onChange={e =>
                    cambiarCampo(
                      "periodo_academico",
                      e.target.value.toUpperCase()
                    )
                  }
                  required
                />
              </div>

              <div className="col-md-4">
                <label className="form-label">
                  Condición{" "}
                  <span className="text-danger">*</span>
                </label>

                <select
                  className="form-select"
                  value={formulario.condicion}
                  onChange={e =>
                    cambiarCampo(
                      "condicion",
                      e.target.value
                    )
                  }
                  required
                >
                  <option value="">
                    Seleccione una condición
                  </option>

                  {CONDICIONES.map(condicion => (
                    <option
                      key={condicion}
                      value={condicion}
                    >
                      {condicion}
                    </option>
                  ))}
                </select>
              </div>

            </div>

            {/* BOTONES DEL REGISTRO */}
            <div className="d-flex gap-2">

              <button
                type="submit"
                className="btn btn-primary px-4"
                disabled={
                  guardando ||
                  (
                    editando === null &&
                    !alumnoSeleccionado
                  )
                }
              >
                <i className="bi bi-floppy-fill me-2" />

                {guardando
                  ? "Guardando..."
                  : editando !== null
                    ? "Actualizar Matrícula"
                    : "Registrar Matrícula"}
              </button>

              <button
                type="button"
                className="btn btn-outline-secondary px-4"
                onClick={limpiarFormulario}
              >
                <i className="bi bi-eraser-fill me-2" />
                Limpiar
              </button>

            </div>

          </form>
        </div>
      </div>

      {/* ====================================
          CONSULTAR MATRÍCULAS
          SOLO DNI Y NOMBRES/APELLIDOS
      ==================================== */}

      <div className="card shadow-sm mb-4">

        <div
          className="card-header fw-bold"
          style={{
            backgroundColor: "#e1f0ff",
            color: "#123f7a",
            fontSize: "1.2rem",
            padding: "15px 20px"
          }}
        >
          <i className="bi bi-list-ul me-2" />
          Consultar Matrículas
        </div>

        <div className="card-body p-4">

          <form
            onSubmit={buscarMatriculas}
            className="row g-3 align-items-end"
          >

            {/* DNI */}
            <div className="col-md-4">
              <label className="form-label">
                DNI
              </label>

              <input
                type="text"
                className="form-control"
                placeholder="Buscar por DNI"
                inputMode="numeric"
                maxLength={8}
                value={filtros.dni}
                onChange={e =>
                  setFiltros({
                    ...filtros,
                    dni: e.target.value
                      .replace(/\D/g, "")
                      .slice(0, 8)
                  })
                }
              />
            </div>

            {/* NOMBRES Y APELLIDOS */}
            <div className="col-md-4">
              <label className="form-label">
                Nombres o apellidos
              </label>

              <input
                type="text"
                className="form-control"
                placeholder="Buscar estudiante"
                maxLength={60}
                value={filtros.nombre}
                onChange={e =>
                  setFiltros({
                    ...filtros,
                    nombre: e.target.value
                      .replace(
                        /[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]/g,
                        ""
                      )
                      .slice(0, 60)
                  })
                }
              />
            </div>

            {/* BOTONES */}
            <div className="col-md-4">
              <div className="d-flex gap-2">

                <button
                  type="submit"
                  className="btn btn-primary"
                  disabled={cargando}
                >
                  <i className="bi bi-search me-1" />
                  Buscar
                </button>

                <button
                  type="button"
                  className="btn btn-outline-secondary"
                  onClick={limpiarFiltros}
                >
                  Limpiar
                </button>

              </div>
            </div>

          </form>
        </div>
      </div>

      {/* ====================================
          RESULTADOS SOLO DESPUÉS DE BUSCAR
      ==================================== */}

      {consultado && (
        <div className="card shadow-sm mb-4">

          <div className="card-body p-4">

            <h5 className="mb-3">
              Resultados de búsqueda
              {" "}({matriculasFiltradas.length})
            </h5>

            {cargando ? (
              <div className="text-center py-4">
                <div
                  className="spinner-border text-primary"
                  role="status"
                />
                <p className="mt-2">
                  Cargando matrículas...
                </p>
              </div>

            ) : matriculasFiltradas.length === 0 ? (
              <div className="alert alert-info">
                No se encontraron matrículas.
              </div>

            ) : (
              <div className="table-responsive">

                <table className="table table-bordered table-hover align-middle">

                  <thead>
                    <tr>
                      {[
                        "ID",
                        "Fecha",
                        "DNI",
                        "Apellidos y nombres",
                        "Carrera",
                        "Turno",
                        "Ciclo",
                        "Periodo",
                        "Condición",
                        "Acciones"
                      ].map(titulo => (
                        <th
                          key={titulo}
                          style={{
                            backgroundColor: "#075aa7",
                            color: "white"
                          }}
                        >
                          {titulo}
                        </th>
                      ))}
                    </tr>
                  </thead>

                  <tbody>
                    {matriculasFiltradas.map(matricula => {
                      const alumno = obtenerAlumnoPorId(
                        matricula.id_alumno
                      );

                      const historica =
                        !matricula.periodo_academico;

                      return (
                        <tr key={matricula.id_matricula}>

                          <td>
                            {matricula.id_matricula}
                          </td>

                          <td>
                            {String(
                              matricula.fecha_matricula
                            ).substring(0, 10)}
                          </td>

                          <td>
                            {mostrarValor(
                              obtenerDni(alumno)
                            )}
                          </td>

                          <td>
                            {mostrarValor(
                              obtenerNombre(alumno)
                            )}
                          </td>

                          <td>
                            {mostrarCarrera(
                              matricula.carrera
                            )}
                          </td>

                          <td>
                            {mostrarValor(
                              matricula.turno
                            )}
                          </td>

                          <td>
                            {mostrarValor(
                              matricula.ciclo
                            )}
                          </td>

                          <td>
                            {mostrarValor(
                              matricula.periodo_academico
                            )}
                          </td>

                          <td>
                            {mostrarValor(
                              matricula.condicion
                            )}
                          </td>

                          <td className="text-nowrap">

                            {historica ? (
                              <span className="badge bg-secondary">
                                Histórico
                              </span>
                            ) : (
                              <button
                                type="button"
                                className="btn btn-warning btn-sm"
                                onClick={() =>
                                  editarMatricula(matricula)
                                }
                              >
                                <i className="bi bi-pencil-fill me-1" />
                                Editar
                              </button>
                            )}

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
