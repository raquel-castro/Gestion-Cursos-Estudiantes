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
    const [cargando, setCargando] = useState(true);
    const [limpiando, setLimpiando] = useState(false);
    const [busqueda, setBusqueda] = useState("");

    const cargarHistorial = async (termino = busqueda) => {
        try {
            setCargando(true);

            const respuesta = await api.get(API_URL, {
                params: termino.trim() ? { buscar: termino.trim() } : undefined
            });

            setLogs(respuesta.data);

        } catch (error) {
            console.error(
                "Error al obtener historial:",
                error
            );

            alertaError(
                error.response?.data?.detail ||
                "No se pudo obtener el historial desde la API."
            );
        } finally {
            setCargando(false);
        }
    };

    useEffect(() => {
        cargarHistorial();
    }, []);

    const buscarHistorial = async (e) => {
        e.preventDefault();
        await cargarHistorial(busqueda);
    };

    const limpiarBusqueda = async () => {
        setBusqueda("");
        await cargarHistorial("");
    };

    const limpiarHistorial = async () => {
        const confirmado = await confirmarAccion(
            "¿Está seguro de que desea limpiar todo el historial?"
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
            console.error(
                "Error al limpiar historial:",
                error
            );

            alertaError(
                error.response?.data?.detail ||
                "No se pudo limpiar el historial desde la API."
            );
        } finally {
            setLimpiando(false);
        }
    };

    const obtenerClaseNivel = (nivel) => {
        const nivelTexto = String(
            nivel || ""
        ).toUpperCase();

        if (nivelTexto === "WARNING") {
            return "historial-level-warning";
        }

        if (nivelTexto === "ERROR") {
            return "historial-level-error";
        }

        return "historial-level-info";
    };

    return (
        <div className="historial-page">

            <div className="historial-header">
                <div>
                    <h1>Historial del Sistema</h1>

                    <p>
                        Registro de actividades realizadas en el sistema
                    </p>
                </div>
            </div>

            <div className="historial-card">

                <div className="historial-card-header">

                    <div className="historial-card-title">
                        <h2>
                            Eventos registrados
                        </h2>

                        <p>
                            Actividades generadas por el sistema.
                        </p>
                    </div>

                    <div className="page-count-badge">
                        {logs.length}
                    </div>

                </div>

                <div className="historial-actions">

                    <button
                        type="button"
                        className="historial-refresh"
                        onClick={cargarHistorial}
                        disabled={cargando}
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

                <form className="historial-search" onSubmit={buscarHistorial}>
                    <label htmlFor="buscar-historial">Buscar en historial</label>
                    <div className="historial-search-row">
                        <div className="historial-search-input">
                            <i className="bi bi-search" aria-hidden="true"></i>
                            <input
                                id="buscar-historial"
                                type="text"
                                placeholder="Buscar por hora, nivel o descripción..."
                                value={busqueda}
                                onChange={(e) => setBusqueda(e.target.value)}
                            />
                        </div>
                        <button type="submit" className="btn btn-primary" disabled={cargando}>
                            <i className="bi bi-search"></i> Buscar
                        </button>
                        <button type="button" className="btn btn-outline-secondary" onClick={limpiarBusqueda} disabled={cargando}>
                            Limpiar
                        </button>
                    </div>
                </form>

                {cargando && (
                    <div className="historial-empty">

                        <div className="historial-empty-icon">
                            ⏳
                        </div>

                        <p>
                            Cargando historial...
                        </p>

                    </div>
                )}

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

                                        const nivel =
                                            String(
                                                log.nivel ||
                                                "INFO"
                                            ).toUpperCase();

                                        return (
                                            <tr key={index}>

                                                <td className="historial-time">
                                                    {log.hora}
                                                </td>

                                                <td>
                                                    <span
                                                        className={
                                                            `historial-level ${obtenerClaseNivel(
                                                                nivel
                                                            )}`
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
