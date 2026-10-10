import Swal from "sweetalert2";

/* =========================================================
   ALERTA DE ÉXITO
========================================================= */

export const alertaExito = (mensaje) => {

    return Swal.fire({
        icon: "success",
        title: "Operación exitosa",
        text: mensaje,
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#183f7a"
    });

};


/* =========================================================
   ALERTA DE ERROR
========================================================= */

export const alertaError = (mensaje) => {

    return Swal.fire({
        icon: "error",
        title: "Error",
        text: mensaje,
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#183f7a"
    });

};


/* =========================================================
   ALERTA DE ADVERTENCIA
========================================================= */

export const alertaAdvertencia = (mensaje) => {

    return Swal.fire({
        icon: "warning",
        title: "Advertencia",
        text: mensaje,
        confirmButtonText: "Aceptar",
        confirmButtonColor: "#183f7a"
    });

};


/* =========================================================
   CONFIRMACIÓN
========================================================= */

export const confirmarAccion = async (mensaje) => {

    const resultado = await Swal.fire({
        icon: "warning",
        title: "¿Está seguro?",
        text: mensaje,
        showCancelButton: true,
        confirmButtonText: "Sí, continuar",
        cancelButtonText: "Cancelar",
        confirmButtonColor: "#dc3545",
        cancelButtonColor: "#6c757d",
        reverseButtons: true
    });

    return resultado.isConfirmed;

};
