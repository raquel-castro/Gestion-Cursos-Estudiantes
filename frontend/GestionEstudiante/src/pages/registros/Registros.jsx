
import { useEffect, useState } from "react";
import api from "../../api/axios";
import "./registros.css";

import {
  alertaExito,
  alertaError,
  confirmarAccion
} from "../../utils/alertas";

const API_URL = "/logs/";

function Historial() {
  const [logs, setLogs] = useState([]);
  const [cargando, setCargando] = useState(false);
  const [limpiando, setLimpiando] = useState(false);
  const [busqueda, setBusqueda] = useState("");

  // ==========================================
  // OBTENER HISTORIAL
  // ==========================================

  const cargarHistorial = async (termino = "") => {
    try {
      setCargando(true);

      const texto = String(termino || "").trim();

      const respuesta = await api.get(API_URL, {
        params: texto ? { buscar: texto } : {}
      });

      if (!Array.isArray(respuesta.data)) {
        throw new Error(
          "La API no devolvió una lista de registros."
        );
      }

      setLogs(respuesta.data);

    } catch (error) {
      console.error("Error al obtener historial:", error);

      const detalle = error.response?.data?.detail;

      alertaError(
        typeof detalle === "string"
          ? detalle
          : error.message ===
            "La API no devolvió una lista de registros."
            ? error.message
            : "No se pudo obtener el historial desde la API."
      );

    } finally {
      setCargando(false);
    }
  };

  // ==========================================
  // CARGAR AL ABRIR LA PÁGINA
  // ==========================================

  useEffect(() => {
    cargarHistorial("");
  }, []);

  // ==========================================
  // BUSCAR HISTORIAL
  // ==========================================

  const buscarHistorial = async (e) => {
    e.preventDefault();
    await cargarHistorial(busqueda);
  };

  // ==========================================
  // LIMPIAR BÚSQUEDA
  // ==========================================

  const limpiarBusqueda = async () => {
    setBusqueda("");
    await cargarHistorial("");
  };

  // ==========================================
  // ACTUALIZAR HISTORIAL
  // ==========================================

  const actualizarHistorial = async () => {
    await cargarHistorial(busqueda);
  };

  // ==========================================
  // LIMPIAR HISTORIAL
  // ==========================================

  const limpiarHistorial = async () => {
    const confirmado = await confirmarAccion(
      "¿Está seguro de que desea eliminar todo el historial?"
    );

    if (!confirmado) return;

    try {
      setLimpiando(true);

      await api.delete(API_URL);

      setLogs([]);

      alertaExito(
        "Historial eliminado correctamente."
      );

    } catch (error) {
      console.error("Error al limpiar historial:", error);

      const detalle = error.response?.data?.detail;

      alertaError(
        typeof detalle === "string"
          ? detalle
          : "No se pudo limpiar el historial desde la API."
      );

    } finally {
      setLimpiando(false);
    }
  };

  // ==========================================
  // COLORES SEGÚN NIVEL
  // ==========================================

  const obtenerClaseNivel = (nivel) => {
    const texto = String(nivel || "").toUpperCase();

    if (texto === "WARNING") {
      return "historial-level-warning";
    }

    if (texto === "ERROR") {
      return "historial-level-error";
    }

    return "historial-level-info";
  };

  // ==========================================
  // INTERFAZ
  // ==========================================

  return (
    <div className="historial-page">

      {/* ENCABEZADO */}
      <div className="historial-header">
        <div>
          <h1>Historial del Sistema</h1>

          <p>
            Registro de actividades realizadas en el sistema
          </p>
        </div>
      </div>

      {/* TARJETA PRINCIPAL */}
      <div className="historial-card">

        <div className="historial-card-header">

          <div className="historial-card-title">
            <h2>Eventos registrados</h2>

            <p>
              Actividades generadas por el sistema.
            </p>
          </div>

          <div className="page-count-badge">
            {logs.length}
          </div>

        </div>

        {/* BOTONES */}
        <div className="historial-actions">

          <button
            type="button"
            className="historial-refresh"
            onClick={actualizarHistorial}
            disabled={cargando || limpiando}
          >
            ↻{" "}
            {cargando
              ? "Actualizando..."
              : "Actualizar"}
          </button>

          <button
            type="button"
            className="historial-clear"
            onClick={limpiarHistorial}
            disabled={
              limpiando ||
              cargando ||
              logs.length === 0
            }
          >
            🗑️{" "}
            {limpiando
              ? "Limpiando..."
              : "Limpiar historial"}
          </button>

        </div>

        {/* BUSCADOR */}
        <form
          className="historial-search"
          onSubmit={buscarHistorial}
        >
          <label htmlFor="buscar-historial">
            Buscar en historial
          </label>

          <div className="historial-search-row">

            <div className="historial-search-input">

              <i
                className="bi bi-search"
                aria-hidden="true"
              />

              <input
                id="buscar-historial"
                type="text"
                placeholder="Buscar por hora, nivel o descripción..."
                value={busqueda}
                onChange={(e) =>
                  setBusqueda(e.target.value)
                }
              />

            </div>

            <button
              type="submit"
              className="btn btn-primary"
              disabled={cargando || limpiando}
            >
              <i className="bi bi-search" />
              {" "}Buscar
            </button>

            <button
              type="button"
              className="btn btn-outline-secondary"
              onClick={limpiarBusqueda}
              disabled={cargando || limpiando}
            >
              Limpiar
            </button>

          </div>
        </form>

        {/* CARGANDO */}
        {cargando && (
          <div className="historial-empty">

            <div className="historial-empty-icon">
              ⏳
            </div>

            <p>Cargando historial...</p>

          </div>
        )}

        {/* SIN RESULTADOS */}
        {!cargando && logs.length === 0 && (
          <div className="historial-empty">

            <div className="historial-empty-icon">
              📋
            </div>

            <p>
              No hay eventos registrados todavía.
            </p>

          </div>
        )}

        {/* TABLA */}
        {!cargando && logs.length > 0 && (
          <div className="historial-table-container">

            <table className="historial-table">

              <thead>
                <tr>
                  <th>Hora</th>
                  <th>Nivel</th>
                  <th>Mensaje</th>
                </tr>
              </thead>

              <tbody>

                {logs
                  .slice()
                  .reverse()
                  .map((log, index) => {

                    const nivel = String(
                      log.nivel || "INFO"
                    ).toUpperCase();

                    return (
                      <tr key={index}>

                        <td className="historial-time">
                          {log.hora}
                        </td>

                        <td>
                          <span
                            className={
                              `historial-level ${obtenerClaseNivel(nivel)}`
                            }
                          >
                            {nivel}
                          </span>
                        </td>

                        <td className="historial-message">
                          {log.msg}
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
  );
}

export default Historial;
