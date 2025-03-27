document.addEventListener('DOMContentLoaded', function () {
    let diasAgregados = 1; // Inicialmente solo Día 1

    // Comprobar si los campos de Día 2 y Día 3 tienen valor al cargar la página
    function checkCamposExistentes() {
        // Verificar si el Día 2 tiene algún valor
        if (document.getElementById("id_I_DiaID2").value) {
            document.getElementById("dia2-fields").style.display = "block"; // Mostrar Día 2
            diasAgregados = 2;  // Actualizar el contador
        }

        // Verificar si el Día 3 tiene algún valor
        if (document.getElementById("id_I_DiaID3").value) {
            document.getElementById("dia3-fields").style.display = "block"; // Mostrar Día 3
            diasAgregados = 3;  // Actualizar el contador
        }

        // Deshabilitar botón de agregar si ya no hay más días para agregar
        if (diasAgregados >= 3) {
            document.getElementById("agregarDiaBtn").disabled = true;
        }

        // Siempre habilitar el botón de eliminar si hay más de un día
        if (diasAgregados > 1) {
            document.getElementById("eliminarDiaBtn").disabled = false;
        }

        console.log("Días agregados al cargar la página: ", diasAgregados);
    }

    // Función para agregar un día
    function agregarDia() {
        if (diasAgregados === 1) {
            document.getElementById("dia2-fields").style.display = "block";
            diasAgregados++;  // Incrementar a 2
        } else if (diasAgregados === 2) {
            document.getElementById("dia3-fields").style.display = "block";
            diasAgregados++;  // Incrementar a 3
        }

        // Deshabilitar el botón de agregar cuando ya no haya más días
        if (diasAgregados >= 3) {
            document.getElementById("agregarDiaBtn").disabled = true;
        }

        // Habilitar el botón de eliminar
        document.getElementById("eliminarDiaBtn").disabled = false;

        console.log("Días agregados después de agregar: ", diasAgregados);
    }

    // Función para eliminar un día
    function eliminarDia() {
        if (diasAgregados === 3) {
            // Limpiar los valores de los campos del Día 3 antes de ocultarlo
            document.getElementById("id_I_DiaID3").value = '';  // Limpiar el campo
            document.getElementById("id_D_HoraInicio3").value = '';  // Limpiar el campo
            document.getElementById("id_D_HoraFin3").value = '';  // Limpiar el campo
    
            document.getElementById("dia3-fields").style.display = "none";
            diasAgregados--;  // Decrementar a 2
        } else if (diasAgregados === 2) {
            // Limpiar los valores de los campos del Día 2 antes de ocultarlo
            document.getElementById("id_I_DiaID2").value = '';  // Limpiar el campo
            document.getElementById("id_D_HoraInicio2").value = '';  // Limpiar el campo
            document.getElementById("id_D_HoraFin2").value = '';  // Limpiar el campo
    
            document.getElementById("dia2-fields").style.display = "none";
            diasAgregados--;  // Decrementar a 1
        } 
    
        // Si no hay más días agregados, deshabilitar el botón de eliminar
        if (diasAgregados <= 1) {
            document.getElementById("eliminarDiaBtn").disabled = true;
        }
    
        // Habilitar el botón de agregar si no se han agregado 3 días
        if (diasAgregados < 3) {
            document.getElementById("agregarDiaBtn").disabled = false;
        }
    
        console.log("Días agregados después de eliminar: ", diasAgregados);
    }
    

    // Asignar los event listeners para los botones de agregar y eliminar
    document.getElementById("agregarDiaBtn").addEventListener('click', agregarDia);
    document.getElementById("eliminarDiaBtn").addEventListener('click', eliminarDia);

    // Verificar los campos existentes cuando la página se carga
    checkCamposExistentes();

    // Asignar el comportamiento del formulario para evitar el envío para depuración
    const form = document.querySelector('form');
    form.addEventListener('submit', function (event) {
        event.preventDefault();  // Prevenir el envío para depuración
        console.log("Formulario enviado con los siguientes datos:");
        console.log(new FormData(form));  // Mostrar los datos del formulario en consola
        form.submit();  // Enviar el formulario después de la depuración
    });
});