import { useEffect, useState } from "react";
import api from "../../api/axios";

import "./dashboard.css";

import {
    alertaError
} from "../../utils/alertas";

function Dashboard({ cambiarPagina }) {
    const [actividades, setActividades] = useState([]);

    const [estadisticas, setEstadisticas] = useState({
        personas: 0,
        alumnos: 0,
        docentes: 0,
        cursos: 0,
        distritos: 0,
        matriculas: 0
    });

    const cargarEstadisticas = async () => {
        try {
            const [
                personas,
                alumnos,
                docentes,
                cursos,
                distritos,
                matriculas
            ] = await Promise.all([
                api.get("/personas/"),
                api.get("/alumnos/"),
                api.get("/docentes/"),
                api.get("/cursos/"),
                api.get("/distritos/"),
                api.get("/matriculas/")
            ]);

            setEstadisticas({
                personas: personas.data.length,
                alumnos: alumnos.data.length,
                docentes: docentes.data.length,
                cursos: cursos.data.length,
                distritos: distritos.data.length,
                matriculas: matriculas.data.length
            });

            try {
                const logs = await api.get("/logs/");
                setActividades(logs.data.slice(-4).reverse());
            } catch (error) {
                console.error("Error al cargar actividad reciente:", error);
                setActividades([]);
            }

        } catch (error) {
            console.error(
                "Error al cargar estadísticas:",
                error
            );

            alertaError(
                "No se pudieron cargar las estadísticas del sistema."
            );
        }
    };

    useEffect(() => {
        cargarEstadisticas();
    }, []);

    return (
        <div className="dashboard-page">

            <div className="dashboard-cards">

                <div className="dashboard-card card-personas">
                    <div className="dashboard-card-icon">
                        👥
                    </div>

                    <div>
                        <span>Personas</span>
                        <strong>
                            {estadisticas.personas}
                        </strong>
                        <small>
                            Personas registradas
                        </small>
                    </div>
                </div>

                <div className="dashboard-card card-alumnos">
                    <div className="dashboard-card-icon">
                        🎓
                    </div>

                    <div>
                        <span>Alumnos</span>
                        <strong>
                            {estadisticas.alumnos}
                        </strong>
                        <small>
                            Alumnos registrados
                        </small>
                    </div>
                </div>

                <div className="dashboard-card card-docentes">
                    <div className="dashboard-card-icon">
                        👨‍🏫
                    </div>

                    <div>
                        <span>Docentes</span>
                        <strong>
                            {estadisticas.docentes}
                        </strong>
                        <small>
                            Docentes registrados
                        </small>
                    </div>
                </div>

                <div className="dashboard-card card-cursos">
                    <div className="dashboard-card-icon">
                        📚
                    </div>

                    <div>
                        <span>Cursos</span>
                        <strong>
                            {estadisticas.cursos}
                        </strong>
                        <small>
                            Cursos registrados
                        </small>
                    </div>
                </div>

                <div className="dashboard-card card-distritos">
                    <div className="dashboard-card-icon">
                        📍
                    </div>

                    <div>
                        <span>Distritos</span>
                        <strong>
                            {estadisticas.distritos}
                        </strong>
                        <small>
                            Distritos registrados
                        </small>
                    </div>
                </div>

                <div className="dashboard-card card-matriculas">
                    <div className="dashboard-card-icon">
                        📝
                    </div>

                    <div>
                        <span>Matrículas</span>
                        <strong>
                            {estadisticas.matriculas}
                        </strong>
                        <small>
                            Matrículas registradas
                        </small>
                    </div>
                </div>

            </div>

            <div className="dashboard-section">

                <h2>
                    Acceso rápido
                </h2>

                <p>
                    Accede rápidamente a las diferentes áreas del sistema.
                </p>

                <div className="quick-actions">

                    <button
                        type="button"
                        onClick={() =>
                            cambiarPagina("personas")
                        }
                    >
                        👥 Ver Personas
                    </button>

                    <button
                        type="button"
                        onClick={() =>
                            cambiarPagina("distritos")
                        }
                    >
                        📍 Ver Distritos
                    </button>

                    <button
                        type="button"
                        onClick={() =>
                            cambiarPagina("alumnos")
                        }
                    >
                        🎓 Ver Alumnos
                    </button>

                    <button
                        type="button"
                        onClick={() =>
                            cambiarPagina("docentes")
                        }
                    >
                        👨‍🏫 Ver Docentes
                    </button>

                    <button
                        type="button"
                        onClick={() =>
                            cambiarPagina("cursos")
                        }
                    >
                        📚 Ver Cursos
                    </button>

                    <button
                        type="button"
                        onClick={() =>
                            cambiarPagina("matriculas")
                        }
                    >
                        📝 Ver Matrículas
                    </button>

                </div>

            </div>

            <div className="dashboard-section activity-section">

                <div className="section-header">

                    <div>
                        <h2>
                            Actividad reciente
                        </h2>

                        <p>
                            Últimas actividades realizadas en el sistema.
                        </p>
                    </div>

                </div>

                <div className="activity-list">
                    {actividades.length === 0 ? (
                        <div className="activity-item">
                            <span className="activity-icon">📋</span>
                            <div className="activity-info">
                                <strong>Sin actividad reciente</strong>
                                <span>No hay eventos registrados.</span>
                            </div>
                        </div>
                    ) : (
                        actividades.map((log, index) => (
                            <div className="activity-item" key={`${log.hora}-${index}`}>
                                <span className="activity-icon">📋</span>
                                <div className="activity-info">
                                    <strong>{log.msg || "Actividad del sistema"}</strong>
                                    <span>{log.nivel || "INFO"}</span>
                                </div>
                                <span className="activity-time">
                                    {log.hora || "Reciente"}
                                </span>
                            </div>
                        ))
                    )}
                </div>

            </div>

        </div>
    );
}

export default Dashboard;
