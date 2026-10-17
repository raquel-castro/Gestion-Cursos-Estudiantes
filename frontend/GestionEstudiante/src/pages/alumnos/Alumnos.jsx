
import { useEffect, useMemo, useState } from "react";
import api from "../../api/axios";
import "./alumnos.css";

import {
  alertaExito,
  alertaError,
  alertaAdvertencia,
  confirmarAccion
} from "../../utils/alertas";

const API_URL = "/alumnos/";

const CARRERAS = [
  { valor: "CONTABILIDAD", texto: "CONTABILIDAD" },
  { valor: "ADMINISTRACION", texto: "ADMINISTRACIÓN" },
  {
    valor: "DESARROLLO DE SISTEMAS DE INFORMACION",
    texto: "DESARROLLO DE SISTEMAS DE INFORMACIÓN"
  }
];

const TURNOS = ["MAÑANA", "NOCHE"];

const FORMULARIO_VACIO = {
  dni: "",
  carrera: "",
  turno_actual: ""
};

const FILTROS_VACIOS = {
  dni: "",
  nombre: ""
};

function obtenerError(error, respaldo) {
  const detalle = error?.response?.data?.detail;

  if (typeof detalle === "string") {
    return detalle;
  }

  if (Array.isArray(detalle)) {
    return detalle
      .map((item) => item.msg || "Dato inválido")
      .join(". ");
  }

  return respaldo;
}

function Alumnos() {
  const [alumnos, setAlumnos] = useState([]);
  const [personas, setPersonas] = useState([]);

  const [formulario, setFormulario] = useState({
    ...FORMULARIO_VACIO
  });

  const [personaSeleccionada, setPersonaSeleccionada] =
    useState(null);

  const [filtros, setFiltros] = useState({
    ...FILTROS_VACIOS
  });

  const [filtrosAplicados, setFiltrosAplicados] = useState({
    ...FILTROS_VACIOS
  });

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

      const [respuestaAlumnos, respuestaPersonas] =
        await Promise.all([
          api.get(API_URL),
          api.get("/personas/")
        ]);

      setAlumnos(respuestaAlumnos.data);
      setPersonas(respuestaPersonas.data);

    } catch (error) {
      alertaError(
        obtenerError(
          error,
          "No se pudieron cargar los alumnos."
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
  // BUSCAR PERSONA POR DNI
  // ==========================================

  const buscarPersona = async () => {
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
        `${API_URL}persona/${dni}`
      );

      setPersonaSeleccionada(respuesta.data);

    } catch (error) {
      setPersonaSeleccionada(null);

      alertaError(
        obtenerError(
          error,
          "Persona no registrada. Regístrela primero."
        )
      );

    } finally {
      setBuscando(false);
    }
  };

  const cambiarDni = (valor) => {
    const dni = valor.replace(/\D/g, "").slice(0, 8);

    setFormulario((anterior) => ({
      ...anterior,
      dni
    }));

    setPersonaSeleccionada(null);
  };

  const cambiarCampo = (campo, valor) => {
    setFormulario((anterior) => ({
      ...anterior,
      [campo]: valor
    }));
  };

  const limpiarFormulario = () => {
    setFormulario({
      ...FORMULARIO_VACIO
    });

    setPersonaSeleccionada(null);
    setEditando(null);
  };

  // ==========================================
  // REGISTRAR Y ACTUALIZAR
  // ==========================================

  const guardarAlumno = async (evento) => {
    evento.preventDefault();

    if (!personaSeleccionada) {
      alertaAdvertencia(
        "Primero busque una persona por DNI."
      );
      return;
    }

    if (!formulario.carrera || !formulario.turno_actual) {
      alertaAdvertencia(
        "Seleccione la carrera y el turno."
      );
      return;
    }

    const datos = {
      carrera: formulario.carrera,
      turno_actual: formulario.turno_actual
    };

    try {
      setGuardando(true);

      if (editando !== null) {
        await api.put(
          `${API_URL}${editando}`,
          datos
        );

        alertaExito(
          "Alumno actualizado correctamente."
        );

      } else {
        await api.post(API_URL, {
          dni: formulario.dni,
          ...datos
        });

        alertaExito(
          "Alumno registrado correctamente."
        );
      }

      limpiarFormulario();
      await cargarDatos();

    } catch (error) {
      alertaError(
        obtenerError(
          error,
          "No se pudo guardar el alumno."
        )
      );

    } finally {
      setGuardando(false);
    }
  };

  // ==========================================
  // EDITAR ALUMNO
  // ==========================================

  const editarAlumno = (alumno) => {
    const persona = personas.find(
      (item) => item.id_persona === alumno.id_persona
    );

    const dni = String(
      alumno.dni || persona?.dni || ""
    );

    setFormulario({
      dni,
      carrera: alumno.carrera || "",
      turno_actual: alumno.turno_actual || ""
    });

    setPersonaSeleccionada(
      persona
        ? {
            dni: persona.dni,
            nombres: persona.nombres,
            apellidos: persona.apellidos
          }
        : {
            dni,
            nombres: alumno.nombre_completo || "",
            apellidos: ""
          }
    );

    setEditando(alumno.id_alumno);

    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  };

  // ==========================================
  // ELIMINAR ALUMNO
  // ==========================================

  const eliminarAlumno = async (alumno) => {
    const confirmado = await confirmarAccion(
      `¿Desea eliminar al alumno ${
        alumno.nombre_completo || alumno.dni
      }?`
    );

    if (!confirmado) return;

    try {
      await api.delete(
        `${API_URL}${alumno.id_alumno}`
      );

      alertaExito(
        "Alumno eliminado correctamente."
      );

      if (editando === alumno.id_alumno) {
        limpiarFormulario();
      }

      await cargarDatos();

    } catch (error) {
      alertaError(
        obtenerError(
          error,
          "No se pudo eliminar el alumno."
        )
      );
    }
  };

  // ==========================================
  // FILTROS
  // ==========================================

  const alumnosFiltrados = useMemo(() => {
    const dniBuscado = filtrosAplicados.dni.trim();

    const nombreBuscado = filtrosAplicados.nombre
      .trim()
      .toLocaleLowerCase("es");

    return alumnos.filter((alumno) => {
      const persona = personas.find(
        (item) => item.id_persona === alumno.id_persona
      );

      const dni = String(
        alumno.dni || persona?.dni || ""
      );

      const nombre = persona
        ? `${persona.apellidos} ${persona.nombres}`
        : alumno.nombre_completo || "";

      return (
        dni.includes(dniBuscado) &&
        nombre
          .toLocaleLowerCase("es")
          .includes(nombreBuscado)
      );
    });
  }, [alumnos, personas, filtrosAplicados]);

  const buscarAlumnos = (evento) => {
    evento.preventDefault();

    setFiltrosAplicados({
      ...filtros
    });
  };

  const limpiarFiltros = () => {
    setFiltros({
      ...FILTROS_VACIOS
    });

    setFiltrosAplicados({
      ...FILTROS_VACIOS
    });
  };

  const mostrarValor = (valor) => valor || "—";

  const mostrarCarrera = (valor) =>
    CARRERAS.find(
      (carrera) => carrera.valor === valor
    )?.texto || mostrarValor(valor);

  const nombreCompleto = personaSeleccionada
    ? `${personaSeleccionada.apellidos} ${personaSeleccionada.nombres}`
        .trim()
    : "";

  // ==========================================
  // INTERFAZ
  // ==========================================

  return (
    <div className="alumnos-page container-fluid">

      <div className="mb-4">
        <h1 className="fw-bold">Alumnos</h1>
        <p className="text-muted">
          Gestión de alumnos registrados
        </p>
      </div>

      {/* REGISTRAR ALUMNO */}
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
          <i className="bi bi-person-plus-fill me-2" />
          {editando !== null
            ? "Editar Alumno"
            : "Registrar Alumno"}
        </div>

        <div className="card-body p-4">

          <form onSubmit={guardarAlumno}>

            {/* DNI Y NOMBRE */}
            <div className="row g-3 mb-3">

              <div className="col-lg-5">
                <label className="form-label fw-semibold">
                  DNI / Código del Estudiante
                  <span className="text-danger"> *</span>
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
                    onChange={(e) =>
                      cambiarDni(e.target.value)
                    }
                    required
                  />

                  <button
                    type="button"
                    className="btn btn-primary"
                    onClick={buscarPersona}
                    disabled={
                      buscando || editando !== null
                    }
                  >
                    <i className="bi bi-search me-2" />
                    {buscando ? "Buscando..." : "Buscar"}
                  </button>

                </div>
              </div>

              <div className="col-lg-7">
                <label className="form-label fw-semibold">
                  Apellidos y nombres
                </label>

                <input
                  type="text"
                  className="form-control"
                  value={nombreCompleto}
                  readOnly
                  placeholder="Se completa al buscar el DNI"
                  style={{
                    backgroundColor: "#e9ecef"
                  }}
                />
              </div>

            </div>

            {/* CARRERA Y TURNO */}
            <div className="row g-3 mb-4">

              <div className="col-md-6">
                <label className="form-label fw-semibold">
                  Carrera
                  <span className="text-danger"> *</span>
                </label>

                <select
                  className="form-select"
                  value={formulario.carrera}
                  onChange={(e) =>
                    cambiarCampo(
                      "carrera",
                      e.target.value
                    )
                  }
                  required
                >
                  <option value="">
                    Seleccione una carrera
                  </option>

                  {CARRERAS.map((carrera) => (
                    <option
                      key={carrera.valor}
                      value={carrera.valor}
                    >
                      {carrera.texto}
                    </option>
                  ))}
                </select>
              </div>

              <div className="col-md-6">
                <label className="form-label fw-semibold">
                  Turno
                  <span className="text-danger"> *</span>
                </label>

                <select
                  className="form-select"
                  value={formulario.turno_actual}
                  onChange={(e) =>
                    cambiarCampo(
                      "turno_actual",
                      e.target.value
                    )
                  }
                  required
                >
                  <option value="">
                    Seleccione un turno
                  </option>

                  {TURNOS.map((turno) => (
                    <option key={turno} value={turno}>
                      {turno}
                    </option>
                  ))}
                </select>
              </div>

            </div>

            {/* BOTONES */}
            <div className="d-flex gap-2">

              <button
                type="submit"
                className="btn btn-primary px-4"
                disabled={
                  guardando || !personaSeleccionada
                }
              >
                <i className="bi bi-floppy-fill me-2" />
                {guardando
                  ? "Guardando..."
                  : editando !== null
                    ? "Actualizar Alumno"
                    : "Registrar Alumno"}
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

      {/* ALUMNOS REGISTRADOS */}
      <div className="card shadow-sm">

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
          Alumnos registrados
        </div>

        <div className="card-body p-4">

          {/* FILTROS */}
          <form
            onSubmit={buscarAlumnos}
            className="row g-3 align-items-end mb-3"
          >

            <div className="col-lg-4">
              <label className="form-label fw-semibold">
                DNI
              </label>

              <input
                type="text"
                className="form-control"
                placeholder="Ej: 71234567"
                inputMode="numeric"
                maxLength={8}
                value={filtros.dni}
                onChange={(e) =>
                  setFiltros({
                    ...filtros,
                    dni: e.target.value
                      .replace(/\D/g, "")
                      .slice(0, 8)
                  })
                }
              />
            </div>

            <div className="col-lg-4">
              <label className="form-label fw-semibold">
                Nombre o apellido
              </label>

              <input
                type="text"
                className="form-control"
                placeholder="Ej: Carlos, Ramírez, Torres"
                value={filtros.nombre}
                onChange={(e) =>
                  setFiltros({
                    ...filtros,
                    nombre: e.target.value
                  })
                }
              />
            </div>

            <div className="col-lg-4">
              <div className="d-flex gap-2">

                <button
                  type="submit"
                  className="btn btn-primary"
                >
                  <i className="bi bi-search me-2" />
                  Buscar
                </button>

                <button
                  type="button"
                  className="btn btn-outline-secondary"
                  onClick={limpiarFiltros}
                >
                  <i className="bi bi-funnel me-2" />
                  Limpiar filtros
                </button>

              </div>
            </div>

          </form>

          {/* TABLA */}
          {cargando ? (

            <div className="text-center py-4">
              <div
                className="spinner-border text-primary"
                role="status"
              />

              <p className="mt-2 text-muted">
                Cargando alumnos...
              </p>
            </div>

          ) : alumnosFiltrados.length === 0 ? (

            <div className="alert alert-info">
              No se encontraron alumnos.
            </div>

          ) : (

            <div className="table-responsive">
              <table className="table table-bordered table-hover align-middle">

                <thead>
                  <tr>
                    {[
                      "DNI",
                      "Apellidos y nombres",
                      "Carrera",
                      "Turno",
                      "Acciones"
                    ].map((titulo) => (
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
                  {alumnosFiltrados.map((alumno) => {
                    const persona = personas.find(
                      (item) =>
                        item.id_persona === alumno.id_persona
                    );

                    const nombre = persona
                      ? `${persona.apellidos} ${persona.nombres}`
                      : alumno.nombre_completo;

                    return (
                      <tr key={alumno.id_alumno}>

                        <td>
                          {mostrarValor(alumno.dni)}
                        </td>

                        <td>
                          {mostrarValor(nombre)}
                        </td>

                        <td>
                          {mostrarCarrera(alumno.carrera)}
                        </td>

                        <td>
                          {mostrarValor(alumno.turno_actual)}
                        </td>

                        <td className="text-nowrap">

                          <button
                            type="button"
                            className="btn btn-warning btn-sm me-2"
                            onClick={() =>
                              editarAlumno(alumno)
                            }
                          >
                            <i className="bi bi-pencil-fill me-1" />
                            Editar
                          </button>

                          <button
                            type="button"
                            className="btn btn-danger btn-sm"
                            onClick={() =>
                              eliminarAlumno(alumno)
                            }
                          >
                            <i className="bi bi-trash-fill me-1" />
                            Eliminar
                          </button>

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

    </div>
  );
}

export default Alumnos;
