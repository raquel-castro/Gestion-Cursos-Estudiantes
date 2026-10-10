import { useEffect, useState } from "react";
import "./header.css";

function Header() {

    const [hora, setHora] = useState(
        new Date().toLocaleTimeString("es-PE")
    );

    const [fecha, setFecha] = useState(
        new Date().toLocaleDateString("es-PE", {
            weekday: "long",
            day: "2-digit",
            month: "long",
            year: "numeric"
        })
    );


    useEffect(() => {

        const intervalo = setInterval(() => {

            const ahora = new Date();

            setHora(
                ahora.toLocaleTimeString("es-PE")
            );

            setFecha(
                ahora.toLocaleDateString("es-PE", {
                    weekday: "long",
                    day: "2-digit",
                    month: "long",
                    year: "numeric"
                })
            );

        }, 1000);

        return () => clearInterval(intervalo);

    }, []);


    return (

        <header className="global-header">

            <div className="global-header-title">

                <h1>
                    Sistema de Gestión de Cursos y Estudiantes
                </h1>

                <p>
                    Panel principal del sistema académico
                </p>

            </div>


            <div className="global-datetime">

                <div className="global-time">

                    <i className="bi bi-clock"></i>

                    {hora}

                </div>

                <div className="global-date">

                    <i className="bi bi-calendar3"></i>

                    {fecha}

                </div>

            </div>

        </header>

    );

}

export default Header;
