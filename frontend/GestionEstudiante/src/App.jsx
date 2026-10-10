import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate, useNavigate } from "react-router-dom";
import Login from "./pages/login/Login";
import Dashboard from "./pages/dashboard/Dashboard";
import Personas from "./pages/personas/Personas";
import Distritos from "./pages/distritos/Distritos";
import Alumnos from "./pages/alumnos/Alumnos";
import Docentes from "./pages/docentes/Docentes";
import Cursos from "./pages/cursos/Cursos";
import Matriculas from "./pages/matriculas/Matriculas";
import Historial from "./pages/registros/Registros";
import Menu from "./components/menu/Menu";
import Header from "./components/header/Header";
import logo from "./assets/logo_1.png";
import { confirmarAccion } from "./utils/alertas";

function Sistema() {
    const navigate = useNavigate();
    const [menuAbierto, setMenuAbierto] = useState(false);

    const cerrarSesion = async () => {
        const confirmado = await confirmarAccion(
            "¿Está seguro de salir del sistema?"
        );

        if (!confirmado) return;

        sessionStorage.removeItem("sesion");
        sessionStorage.removeItem("usuario");
        setMenuAbierto(false);
        navigate("/login", { replace: true });
    };

    const cambiarPagina = (pagina) => {
        navigate(`/${pagina}`);
        setMenuAbierto(false);
    };

    return (
        <div className="app">

            <Menu
                menuAbierto={menuAbierto}
                setMenuAbierto={setMenuAbierto}
                cerrarSesion={cerrarSesion}
                logo={logo}
            />

            <main className="main-content">

                <Header />

                <Routes>

                    <Route
                        path="/dashboard"
                        element={
                            <Dashboard
                                cambiarPagina={cambiarPagina}
                            />
                        }
                    />

                    <Route
                        path="/personas"
                        element={<Personas />}
                    />

                    <Route
                        path="/distritos"
                        element={<Distritos />}
                    />

                    <Route
                        path="/alumnos"
                        element={<Alumnos />}
                    />

                    <Route
                        path="/docentes"
                        element={<Docentes />}
                    />

                    <Route
                        path="/cursos"
                        element={<Cursos />}
                    />

                    <Route
                        path="/matriculas"
                        element={<Matriculas />}
                    />

                    <Route
                        path="/historial"
                        element={<Historial />}
                    />

                    <Route
                        path="*"
                        element={
                            <Navigate
                                to="/dashboard"
                                replace
                            />
                        }
                    />

                </Routes>

            </main>

        </div>
    );
}

function RutaSistema() {
    const sesion = sessionStorage.getItem("sesion");

    if (sesion !== "activa") {
        return (
            <Navigate
                to="/login"
                replace
            />
        );
    }

    return <Sistema />;
}

function App() {
    return (
        <BrowserRouter>

            <Routes>

                <Route
                    path="/login"
                    element={<Login />}
                />

                <Route
                    path="/*"
                    element={<RutaSistema />}
                />

            </Routes>

        </BrowserRouter>
    );
}

export default App;
