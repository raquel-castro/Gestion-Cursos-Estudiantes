
import { useState } from "react";
import api from "../../api/axios";
import "./cursos.css";

import {
  alertaExito,
  alertaError,
  alertaAdvertencia,
  confirmarAccion
} from "../../utils/alertas";

// ==========================================
// OPCIONES
// ==========================================

const CARRERAS = [
  { value: "ADMINISTRACION", label: "Administración" },
  { value: "CONTABILIDAD", label: "Contabilidad" },
  {
    value: "DESARROLLO DE SISTEMAS DE INFORMACION",
    label: "Desarrollo de Sistemas de Información"
  }
];

const CICLOS = ["I", "II", "III", "IV", "V", "VI"];

const VACIO = {
  nombre: "",
  carrera: "",
  ciclo: "",
  descripcion: "",
  creditos: "",
  horas_semanales: ""
};

const FILTROS = {
  nombre: "",
  carrera: "",
  ciclo: ""
};

// ==========================================
// VALIDACIONES
// ==========================================

// Solo letras, tildes, ñ y espacios.
const SOLO_LETRAS = /[^A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]/g;

// Nombre obligatorio: entre 1 y 30 caracteres.
const NOMBRE_VALIDO =
  /^[A-Za-zÁÉÍÓÚÜÑáéíóúüñ ]{1,30}$/;

function limpiarNombre(valor) {
  return valor
    .replace(SOLO_LETRAS, "")
    .slice(0, 30);
}

// Solo un dígito entre 1 y 9.
function validarDigito(valor) {
  return /^[1-9]?$/.test(valor);
}

function obtenerError(error, mensaje) {
  const detalle = error?.response?.data?.detail;

  if (typeof detalle === "string") {
    return detalle;
  }

  if (Array.isArray(detalle)) {
    return detalle
      .map(item => item.msg || "Dato inválido")
      .join(". ");
  }

  return mensaje;
}

// ==========================================
// COMPONENTE PRINCIPAL
// ==========================================

export default function Cursos() {
  const [form, setForm] = useState({ ...VACIO });
  const [filtros, setFiltros] = useState({ ...FILTROS });

  const [resultados, setResultados] = useState([]);
  const [consultado, setConsultado] = useState(false);

  const [editando, setEditando] = useState(null);
  const [cargando, setCargando] = useState(false);
  const [guardando, setGuardando] = useState(false);

  // ==========================================
  // CAMBIAR CAMPOS
  // ==========================================

  const campo = (nombre, valor) => {
    setForm(prev => ({
      ...prev,
      [nombre]: valor
    }));
  };

  const filtro = (nombre, valor) => {
    setFiltros(prev => ({
      ...prev,
      [nombre]: valor
    }));
  };

  const cambiarNombre = valor => {
    campo("nombre", limpiarNombre(valor));
  };

  const cambiarNombreFiltro = valor => {
    filtro("nombre", limpiarNombre(valor));
  };

  const cambiarNumero = (nombre, valor) => {
    if (validarDigito(valor)) {
      campo(nombre, valor);
    }
  };

  // ==========================================
  // LIMPIAR FORMULARIOS
  // ==========================================

  const limpiarForm = () => {
    setForm({ ...VACIO });
    setEditando(null);
  };

  const limpiarFiltros = () => {
    setFiltros({ ...FILTROS });
    setResultados([]);
    setConsultado(false);
  };

  // ==========================================
  // BUSCAR CURSOS
  // ==========================================

  async function buscar(e) {
    e?.preventDefault();
    setCargando(true);

    try {
      const params = {};

      if (filtros.nombre.trim()) {
        params.nombre = filtros.nombre.trim();
      }

      if (filtros.carrera) {
        params.carrera = filtros.carrera;
      }

      if (filtros.ciclo) {
        params.ciclo = filtros.ciclo;
      }

      const url = Object.keys(params).length
        ? "/cursos/buscar"
        : "/cursos/";

      const respuesta = await api.get(
        url,
        Object.keys(params).length
          ? { params }
          : {}
      );

      setResultados(respuesta.data);
      setConsultado(true);

    } catch (error) {
      alertaError(
        obtenerError(
          error,
          "No se pudieron consultar los cursos."
        )
      );

    } finally {
      setCargando(false);
    }
  }

  // ==========================================
  // GUARDAR CURSO
  // ==========================================

  async function guardar(e) {
    e.preventDefault();

    const nombre = form.nombre.trim();
    const creditos = Number(form.creditos);

    const horas =
      form.horas_semanales === ""
        ? null
        : Number(form.horas_semanales);

    if (!NOMBRE_VALIDO.test(nombre)) {
      alertaAdvertencia(
        "El nombre del curso debe contener solo letras y espacios, con un máximo de 30 caracteres."
      );
      return;
    }

    if (!form.carrera || !form.ciclo) {
      alertaAdvertencia(
        "Seleccione la carrera y el semestre."
      );
      return;
    }

    if (
      !Number.isInteger(creditos) ||
      creditos < 1 ||
      creditos > 9
    ) {
      alertaAdvertencia(
        "Los créditos deben ser un número entero del 1 al 9."
      );
      return;
    }

    if (
      horas !== null &&
      (
        !Number.isInteger(horas) ||
        horas < 1 ||
        horas > 9
      )
    ) {
      alertaAdvertencia(
        "Las horas semanales deben ser un número entero del 1 al 9."
      );
      return;
    }

    const datos = {
      nombre,
      carrera: form.carrera,
      ciclo: form.ciclo,
      creditos,
      descripcion: form.descripcion.trim() || null,
      horas_semanales: horas
    };

    setGuardando(true);

    try {
      if (editando !== null) {
        await api.put(
          `/cursos/${editando}`,
          datos
        );

        alertaExito(
          "Curso actualizado correctamente."
        );

      } else {
        await api.post("/cursos/", datos);

        alertaExito(
          "Curso registrado correctamente."
        );
      }

      limpiarForm();

      if (consultado) {
        await buscar();
      }

    } catch (error) {
      alertaError(
        obtenerError(
          error,
          "No se pudo guardar el curso."
        )
      );

    } finally {
      setGuardando(false);
    }
  }

  // ==========================================
  // EDITAR CURSO
  // ==========================================

  function editar(curso) {
    setEditando(curso.id_curso);

    setForm({
      nombre: curso.nombre || "",
      carrera: curso.carrera || "",
      ciclo: curso.ciclo || "",
      descripcion: curso.descripcion || "",
      creditos: String(curso.creditos ?? ""),
      horas_semanales: String(
        curso.horas_semanales ?? ""
      )
    });

    window.scrollTo({
      top: 0,
      behavior: "smooth"
    });
  }

  // ==========================================
  // ELIMINAR CURSO
  // ==========================================

  async function eliminar(curso) {
    const confirmado = await confirmarAccion(
      `¿Eliminar el curso ${curso.nombre}?`
    );

    if (!confirmado) return;

    try {
      await api.delete(
        `/cursos/${curso.id_curso}`
      );

      alertaExito(
        "Curso eliminado correctamente."
      );

      await buscar();

    } catch (error) {
      alertaError(
        obtenerError(
          error,
          "No se pudo eliminar el curso. Puede estar asociado a docentes u otros registros."
        )
      );
    }
  }

  // ==========================================
  // INTERFAZ
  // ==========================================

  return (
    <div className="cursos-page container-fluid px-3 px-md-4 mt-4">

      <h1 className="mb-4">
        Registro de Cursos
      </h1>

      {/* ====================================
          REGISTRAR CURSO
      ==================================== */}

      <div className="card shadow-sm mb-4">

        <div className="card-header bg-primary text-white">
          <h5 className="mb-0">
            {editando !== null
              ? "Editar curso"
              : "Registrar nuevo curso"}
          </h5>
        </div>

        <div className="card-body">
          <form onSubmit={guardar}>

            <div className="row g-3">

              {/* NOMBRE DEL CURSO */}
              <div className="col-md-6">
                <label className="form-label">
                  Nombre del curso{" "}
                  <span className="text-danger">*</span>
                </label>

                <input
                  type="text"
                  className="form-control"
                  placeholder="Nombre del curso"
                  value={form.nombre}
                  maxLength={30}
                  onChange={e =>
                    cambiarNombre(e.target.value)
                  }
                  required
                />

                <small className="text-muted">
                  Solo letras. Máximo 30 caracteres.
                  {" "}({form.nombre.length}/30)
                </small>
              </div>

              {/* CARRERA */}
              <div className="col-md-6">
                <label className="form-label">
                  Carrera{" "}
                  <span className="text-danger">*</span>
                </label>

                <select
                  className="form-select"
                  value={form.carrera}
                  onChange={e =>
                    campo(
                      "carrera",
                      e.target.value
                    )
                  }
                  required
                >
                  <option value="">
                    Seleccione una carrera
                  </option>

                  {CARRERAS.map(c => (
                    <option
                      key={c.value}
                      value={c.value}
                    >
                      {c.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* SEMESTRE */}
              <div className="col-md-4">
                <label className="form-label">
                  Semestre{" "}
                  <span className="text-danger">*</span>
                </label>

                <select
                  className="form-select"
                  value={form.ciclo}
                  onChange={e =>
                    campo("ciclo", e.target.value)
                  }
                  required
                >
                  <option value="">
                    Seleccione semestre
                  </option>

                  {CICLOS.map(c => (
                    <option
                      key={c}
                      value={c}
                    >
                      {c}
                    </option>
                  ))}
                </select>
              </div>

              {/* CRÉDITOS */}
              <div className="col-md-4">
                <label className="form-label">
                  Créditos{" "}
                  <span className="text-danger">*</span>
                </label>

                <input
                  type="number"
                  className="form-control"
                  min="1"
                  max="9"
                  step="1"
                  value={form.creditos}
                  onChange={e =>
                    cambiarNumero(
                      "creditos",
                      e.target.value
                    )
                  }
                  required
                />

                <small className="text-muted">
                  Solo un dígito del 1 al 9.
                </small>
              </div>

              {/* HORAS SEMANALES */}
              <div className="col-md-4">
                <label className="form-label">
                  Horas semanales (opcional)
                </label>

                <input
                  type="number"
                  className="form-control"
                  min="1"
                  max="9"
                  step="1"
                  value={form.horas_semanales}
                  onChange={e =>
                    cambiarNumero(
                      "horas_semanales",
                      e.target.value
                    )
                  }
                />

                <small className="text-muted">
                  Solo un dígito del 1 al 9.
                </small>
              </div>

              {/* DESCRIPCIÓN */}
              <div className="col-12">
                <label className="form-label">
                  Descripción (opcional)
                </label>

                <textarea
                  className="form-control"
                  rows="2"
                  placeholder="Descripción del curso"
                  value={form.descripcion}
                  onChange={e =>
                    campo(
                      "descripcion",
                      e.target.value
                    )
                  }
                />
              </div>

            </div>

            {/* BOTONES */}
            <div className="mt-3 d-flex gap-2">

              <button
                type="submit"
                className="btn btn-primary"
                disabled={guardando}
              >
                {guardando
                  ? "Guardando..."
                  : editando !== null
                    ? "ACTUALIZAR CURSO"
                    : "GRABAR CURSO"}
              </button>

              <button
                type="button"
                className="btn btn-secondary"
                onClick={limpiarForm}
              >
                Limpiar
              </button>

            </div>

          </form>
        </div>
      </div>

      {/* ====================================
          CONSULTAR CURSOS
      ==================================== */}

      <div className="card shadow-sm mb-4">

        <div className="card-header bg-primary text-white">
          <h5 className="mb-0">
            Consultar Cursos
          </h5>
        </div>

        <div className="card-body">
          <form onSubmit={buscar}>

            <div className="row g-3">

              {/* FILTRO NOMBRE */}
              <div className="col-md-4">
                <label className="form-label">
                  Nombre del curso
                </label>

                <input
                  type="text"
                  className="form-control"
                  placeholder="Buscar por nombre"
                  maxLength={30}
                  value={filtros.nombre}
                  onChange={e =>
                    cambiarNombreFiltro(
                      e.target.value
                    )
                  }
                />

                <small className="text-muted">
                  Solo letras. Máximo 30 caracteres.
                </small>
              </div>

              {/* FILTRO CARRERA */}
              <div className="col-md-4">
                <label className="form-label">
                  Carrera
                </label>

                <select
                  className="form-select"
                  value={filtros.carrera}
                  onChange={e =>
                    filtro(
                      "carrera",
                      e.target.value
                    )
                  }
                >
                  <option value="">
                    Todas las carreras
                  </option>

                  {CARRERAS.map(c => (
                    <option
                      key={c.value}
                      value={c.value}
                    >
                      {c.label}
                    </option>
                  ))}
                </select>
              </div>

              {/* FILTRO SEMESTRE */}
              <div className="col-md-4">
                <label className="form-label">
                  Semestre
                </label>

                <select
                  className="form-select"
                  value={filtros.ciclo}
                  onChange={e =>
                    filtro(
                      "ciclo",
                      e.target.value
                    )
                  }
                >
                  <option value="">
                    Todos los semestres
                  </option>

                  {CICLOS.map(c => (
                    <option
                      key={c}
                      value={c}
                    >
                      {c}
                    </option>
                  ))}
                </select>
              </div>

            </div>

            {/* BOTONES DE BÚSQUEDA */}
            <div className="mt-3 d-flex gap-2">

              <button
                type="submit"
                className="btn btn-primary"
                disabled={cargando}
              >
                {cargando
                  ? "Buscando..."
                  : "Buscar"}
              </button>

              <button
                type="button"
                className="btn btn-secondary"
                onClick={limpiarFiltros}
              >
                Limpiar
              </button>

            </div>

          </form>
        </div>
      </div>

      {/* ====================================
          RESULTADOS DE BÚSQUEDA
      ==================================== */}

      {consultado && (
        <div className="card shadow-sm mb-4">

          <div className="card-body">

            <h5 className="mb-3">
              Resultados de búsqueda ({resultados.length})
            </h5>

            {resultados.length === 0 ? (
              <div className="alert alert-info">
                No se encontraron cursos.
              </div>
            ) : (
              <div className="table-responsive">

                <table className="table table-hover align-middle">

                  <thead className="table-light">
                    <tr>
                      <th>Curso</th>
                      <th>Carrera</th>
                      <th>Semestre</th>
                      <th>Créditos</th>
                      <th>Horas semanales</th>
                      <th>Descripción</th>
                      <th>Acciones</th>
                    </tr>
                  </thead>

                  <tbody>
                    {resultados.map(c => (
                      <tr key={c.id_curso}>

                        <td>{c.nombre}</td>

                        <td>
                          {CARRERAS.find(
                            x => x.value === c.carrera
                          )?.label ||
                            c.carrera ||
                            "—"}
                        </td>

                        <td>{c.ciclo}</td>
                        <td>{c.creditos}</td>

                        <td>
                          {c.horas_semanales ?? "—"}
                        </td>

                        <td>
                          {c.descripcion || "—"}
                        </td>

                        <td>
                          <div className="d-flex gap-2">

                            <button
                              type="button"
                              className="btn btn-warning btn-sm"
                              onClick={() => editar(c)}
                            >
                              Editar
                            </button>

                            <button
                              type="button"
                              className="btn btn-danger btn-sm"
                              onClick={() => eliminar(c)}
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
      )}

    </div>
  );
}
