function Busqueda({ campos, onBuscar, onLimpiar, cargando = false }) {
    return (
        <form className="busqueda-card" onSubmit={onBuscar}>
            <div className="busqueda-grid">
                {campos.map((campo) => (
                    <div className="busqueda-field" key={campo.name}>
                        <label htmlFor={`buscar-${campo.name}`}>
                            {campo.label}
                        </label>
                        <div className="busqueda-input-wrap">
                            <i className="bi bi-search busqueda-icon" aria-hidden="true"></i>
                            {campo.type === "select" ? (
                                <select
                                    id={`buscar-${campo.name}`}
                                    name={campo.name}
                                    value={campo.value}
                                    onChange={campo.onChange}
                                >
                                    {campo.options.map((option) => (
                                        <option key={option.value} value={option.value}>
                                            {option.label}
                                        </option>
                                    ))}
                                </select>
                            ) : (
                                <input
                                    id={`buscar-${campo.name}`}
                                    type={campo.type || "text"}
                                    name={campo.name}
                                    min={campo.type === "number" ? "1" : undefined}
                                    placeholder={campo.placeholder}
                                    value={campo.value}
                                    onChange={campo.onChange}
                                />
                            )}
                        </div>
                    </div>
                ))}
            </div>
            <div className="busqueda-actions">
                <button type="submit" className="btn btn-primary" disabled={cargando}>
                    {cargando ? "Buscando..." : "Buscar"}
                </button>
                <button type="button" className="btn btn-outline-secondary" onClick={onLimpiar} disabled={cargando}>
                    Limpiar
                </button>
            </div>
        </form>
    );
}

export default Busqueda;
