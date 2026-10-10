import "./menu.css";
import { useNavigate, useLocation } from "react-router-dom";

function Menu({ menuAbierto, setMenuAbierto, cerrarSesion, logo }) {

    const navigate = useNavigate();
    const location = useLocation();

    const menuItems = [
        {
            id: "dashboard",
            icono: "bi-house",
            texto: "Inicio"
        },
        {
            id: "personas",
            icono: "bi-people",
            texto: "Personas"
        },
        {
            id: "distritos",
            icono: "bi-geo-alt",
            texto: "Distritos"
        },
        {
            id: "alumnos",
            icono: "bi-mortarboard",
            texto: "Alumnos"
        },
        {
            id: "docentes",
            icono: "bi-person-workspace",
            texto: "Docentes"
        },
        {
            id: "cursos",
            icono: "bi-book",
            texto: "Cursos"
        },
        {
            id: "matriculas",
            icono: "bi-journal-check",
            texto: "Matrículas"
        },
        {
            id: "historial",
            icono: "bi-clock-history",
            texto: "Historial"
        }
    ];

    const cambiarPagina = (pagina) => {

        navigate(`/${pagina}`);

        setMenuAbierto(false);
    };

    const paginaActual =
        location.pathname.replace("/", "") || "dashboard";

    return (
        <>
            {/* Botón hamburguesa */}

            <button
                type="button"
                className="menu-toggle"
                onClick={() => setMenuAbierto(!menuAbierto)}
                aria-label="Abrir menú"
            >
                <i
                    className={
                        menuAbierto
                            ? "bi bi-x-lg"
                            : "bi bi-list"
                    }
                ></i>
            </button>


            {/* Overlay */}

            {menuAbierto && (
                <div
                    className="sidebar-overlay"
                    onClick={() => setMenuAbierto(false)}
                />
            )}


            {/* Sidebar */}

            <aside
                className={
                    `sidebar ${
                        menuAbierto
                            ? "sidebar-open"
                            : ""
                    }`
                }
            >

                {/* Logo */}

                <div className="sidebar-header">

                    <img
                        src={logo}
                        alt="Logo Sistema Académico"
                        className="logo-icon"
                    />

                    <h2>
                        Sistema
                        <br />
                        Académico
                    </h2>

                </div>


                {/* Opciones */}

                <nav className="sidebar-menu">

                    {menuItems.map((item) => (

                        <button
                            key={item.id}
                            type="button"
                            className={
                                `menu-item ${
                                    paginaActual === item.id
                                        ? "active"
                                        : ""
                                }`
                            }
                            onClick={() =>
                                cambiarPagina(item.id)
                            }
                        >

                            <span className="menu-icon">
                                <i className={`bi ${item.icono}`}></i>
                            </span>

                            <span>
                                {item.texto}
                            </span>

                        </button>

                    ))}


                    {/* Cerrar sesión */}

                    <button
                        type="button"
                        className="menu-item logout-item"
                        onClick={cerrarSesion}
                    >

                        <span className="menu-icon">
                            <i className="bi bi-box-arrow-right"></i>
                        </span>

                        <span>
                            Cerrar sesión
                        </span>

                    </button>

                </nav>

            </aside>
        </>
    );
}

export default Menu;
