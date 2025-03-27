 const hoy = new Date();
    
 // Opciones de formato en español
 const opciones = { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' };
let fechaFormateada = hoy.toLocaleDateString('es-ES', opciones);
        // Convertir la primera letra en mayúscula
        fechaFormateada = fechaFormateada.charAt(0).toUpperCase() + fechaFormateada.slice(1);

        // Insertar la fecha en el HTML
        document.getElementById("fecha").textContent = fechaFormateada;
