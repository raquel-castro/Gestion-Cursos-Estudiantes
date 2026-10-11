import { useState } from "react";
import { useNavigate } from "react-router-dom";
import "./login.css";
import logo from "../../assets/logo_1.png";
import api from "../../api/axios";

import {
    alertaError,
    alertaAdvertencia,
    alertaExito
} from "../../utils/alertas";

function Login() {
    const navigate = useNavigate();

    const [usuario, setUsuario] = useState("");
    const [contrasena, setContrasena] = useState("");

    const manejarLogin = async (e) => {
        e.preventDefault();

        if (!usuario.trim() || !contrasena) {
            alertaAdvertencia(
                "Ingrese usuario y contraseña."
            );
            return;
        }

        try {
            const response = await api.post("/auth/login", {
                nombre_usuario: usuario.trim(),
                contrasena: contrasena
            });

            sessionStorage.setItem(
                "sesion",
                "activa"
            );

            sessionStorage.setItem(
                "usuario",
                response.data.nombre_usuario
            );

            alertaExito(
                "Inicio de sesión correcto."
            );

            navigate("/dashboard");

        } catch (error) {
            alertaError(
                error.response?.data?.detail ||
                "Usuario o contraseña incorrectos."
            );
        }
    };

    return (
        <div className="login-page">

            <div className="login-container">

                <div className="login-brand">

                    <img
                        src={logo}
                        alt="Sistema Académico"
                        className="login-brand-logo"
                    />

                    <h1 className="login-brand-title">
                        Sistema Académico
                    </h1>

                    <p className="login-brand-description">
                        Gestión de cursos y estudiantes
                    </p>

                    <div className="login-brand-books">
                        📚
                    </div>

                </div>

                <div className="login-right">

                    <div className="login-form-container">

                        <h2>
                            Bienvenido de nuevo
                        </h2>

                        <p className="login-subtitle">
                            Inicia sesión para continuar
                        </p>

                        <form onSubmit={manejarLogin}>

                            <div className="login-field">

                                <label htmlFor="usuario">
                                    Usuario
                                </label>

                                <input
                                    id="usuario"
                                    type="text"
                                    placeholder="Ingresa tu usuario"
                                    value={usuario}
                                    onChange={(e) =>
                                        setUsuario(e.target.value)
                                    }
                                    autoComplete="username"
                                    required
                                />

                            </div>

                            <div className="login-field">

                                <label htmlFor="contrasena">
                                    Contraseña
                                </label>

                                <input
                                    id="contrasena"
                                    type="password"
                                    placeholder="Ingresa tu contraseña"
                                    value={contrasena}
                                    onChange={(e) =>
                                        setContrasena(e.target.value)
                                    }
                                    autoComplete="current-password"
                                    required
                                />

                            </div>

                            <button
                                type="submit"
                                className="login-button"
                            >
                                Iniciar Sesión
                            </button>

                            <div className="login-divider">
                                <span></span>
                                <strong>o</strong>
                                <span></span>
                            </div>

                            <button
                                type="button"
                                className="google-button"
                                onClick={() =>
                                    alertaAdvertencia(
                                        "El inicio de sesión con Google no está disponible."
                                    )
                                }
                            >
                                <span className="google-logo">
                                    G
                                </span>
                                Continuar con Google
                            </button>

                        </form>

                    </div>

                </div>

            </div>

        </div>
    );
}

export default Login;