// Función para obtener las programaciones seleccionadas
function obtenerProgramacionesSeleccionadas() {
    let programacionesSeleccionadas = document.getElementById("programaciones_seleccionadas").value;
    return programacionesSeleccionadas ? JSON.parse(programacionesSeleccionadas) : [];
}

// Función para actualizar las programaciones seleccionadas en el campo oculto
function actualizarProgramacionesSeleccionadas(programaciones) {
    document.getElementById("programaciones_seleccionadas").value = JSON.stringify(programaciones);
}

let sumaCreditosI = 0;
let sumaCreditosII = 0;

// Función para agregar asignaturas seleccionadas
// Función para verificar si ya existe un electivo en el período seleccionado
function existeElectivoEnPeriodo(periodo) {
    const filas = document.querySelectorAll("#tabla_asignaturas_seleccionadas_body tr");
    return Array.from(filas).some(fila => {
        const condicion = fila.cells[4].textContent.trim(); // Columna 5: Condición
        const periodoAsignatura = fila.cells[0].textContent.trim(); // Columna 1: Período
        return condicion === "ELECTIVO" && periodoAsignatura === periodo;
    });
}

// Función para agregar asignaturas seleccionadas
function agregarAsignatura(ID, periodo, codigo, ciclo, nombre, condicion, turno, seccion, vez, creditos, dias, horas, docente, aula) {
    // Convertir ID a array si es una cadena
    if (typeof ID === "string") {
        try {
            ID = JSON.parse(ID);
        } catch (error) {
            return; // Si la conversión falla, salir de la función
        }
    }

    const programacionIDs = Array.isArray(ID) ? ID.map(id => parseInt(id)).filter(id => !isNaN(id)) : [];

    // Verificar si el código ya está en la tabla
    const codigosExistentes = Array.from(document.querySelectorAll("#tabla_asignaturas_seleccionadas_body tr td:nth-child(3)"))
        .map(cell => cell.textContent);

    if (codigosExistentes.includes(codigo)) {
        alert(`La asignatura ${nombre} con el código ${codigo} ya existe. No se agregará nuevamente.`);
        return;
    }

    // Verificar si ya se seleccionó un electivo en el mismo período
    if (condicion === "ELECTIVO" && existeElectivoEnPeriodo(periodo)) {
        alert(`Solo se puede seleccionar un curso ELECTIVO en el PERIODO ${periodo}.`);
        return;
    }

    // Actualizar la lista de programaciones seleccionadas
    const programacionesSeleccionadas = obtenerProgramacionesSeleccionadas();
    programacionesSeleccionadas.push(...programacionIDs);
    actualizarProgramacionesSeleccionadas(programacionesSeleccionadas);

    // Insertar la nueva fila en la tabla
    const tabla = document.getElementById("tabla_asignaturas_seleccionadas_body");
    const fila = tabla.insertRow();
    const celdas = [periodo, ciclo, codigo, nombre, condicion, turno, seccion, vez, creditos, dias, horas, docente, aula];
    
    celdas.forEach((contenido, index) => fila.insertCell(index).innerHTML = contenido);
    
    // Agregar botón de eliminar
    const cellEliminar = fila.insertCell(13);
    const botonEliminar = document.createElement("button");
    botonEliminar.innerHTML = "-";
    botonEliminar.className = "btn-eliminar";
    botonEliminar.onclick = () => eliminarAsignatura(fila, programacionIDs, parseInt(creditos), periodo, codigo);
    cellEliminar.appendChild(botonEliminar);

    // Mostrar la tabla si no está vacía
    document.getElementById("tabla_seleccionadas").style.display = "block";
    ordenarTablaPorPeriodo();

    // Actualizar créditos por período
    if (periodo === "I") {
        sumaCreditosI += parseInt(creditos);
        document.getElementById("creditosI").innerText = sumaCreditosI;
    } else if (periodo === "II") {
        sumaCreditosII += parseInt(creditos);
        document.getElementById("creditosII").innerText = sumaCreditosII;
    }

    // Resaltar la fila en la tabla de asignaturas disponibles
    document.querySelectorAll(".table-disponibles tbody tr").forEach(row => {
        if (row.children[2].textContent.trim() === codigo) {
            row.style.backgroundColor = "#d1e7dd"; // Verde claro
        }
    });
}


// Función para eliminar asignaturas seleccionadas
function eliminarAsignatura(fila, ID, creditos, periodo, cod) {
    // Obtener las programaciones seleccionadas actuales
    const programacionesSeleccionadas = obtenerProgramacionesSeleccionadas();
    console.log("Programaciones seleccionadas antes de la eliminación:", programacionesSeleccionadas);

    // Eliminar los IDs correspondientes
    const programacionesRestantes = programacionesSeleccionadas.filter(item => !ID.includes(item));
    console.log("Programaciones seleccionadas después de la eliminación:", programacionesRestantes);

    // Actualizar el campo oculto con las programaciones restantes
    actualizarProgramacionesSeleccionadas(programacionesRestantes);

    // Eliminar la fila de la tabla
    fila.remove();

    document.querySelectorAll(".table-disponibles tbody tr").forEach(row => {
        const codigoAsignatura = row.children[2].textContent.trim(); // Columna 3 (índice 2) es el código
        if (codigoAsignatura === String(cod)) {
            row.style.backgroundColor = ""; // Restaurar color original (vacío usa el CSS predeterminado)
        }
    });

    // Mostrar u ocultar la tabla según el número de asignaturas restantes
    document.getElementById("tabla_seleccionadas").style.display = programacionesRestantes.length ? "block" : "none";
    
    ordenarTablaPorPeriodo();

    if (periodo === 'I'){
        sumaCreditosI -= creditos;
        document.getElementById("creditosI").innerText = sumaCreditosI;
    }
    if (periodo === 'II'){
        sumaCreditosII -= creditos;
        document.getElementById("creditosII").innerText = sumaCreditosII;
    }
}

function ordenarTablaPorPeriodo() {
    const tabla = document.getElementById("tabla_asignaturas_seleccionadas_body");
    const filas = Array.from(tabla.querySelectorAll("tr"));

    filas.sort((a, b) => {
        const periodoA = a.cells[0].textContent;
        const periodoB = b.cells[0].textContent;
        return periodoA.localeCompare(periodoB);
    });

    filas.forEach(fila => tabla.appendChild(fila));
}

let shouldWarnOnUnload = true;

// Escucha el evento beforeunload
window.addEventListener("beforeunload", function (event) {
    if (shouldWarnOnUnload) {
        event.preventDefault();
        event.returnValue = "¿Estás seguro de que deseas salir de esta página? Se perderán los cambios no guardados.";
    }
});

// Maneja el clic en el botón con la clase registrar-button
document.querySelector(".registrar-button").addEventListener("click", function () {
    shouldWarnOnUnload = false; // Desactiva la advertencia temporalmente
});

function filtrarBotonRegistrar() {
    const programacionesSeleccionadas = obtenerProgramacionesSeleccionadas();
    const cantidadProgramaciones = programacionesSeleccionadas.length;
    
    if (mayorCuatro()){
        if (cantidadProgramaciones === 0) {
            alert('No ha seleccionado una asignatura');
            event.preventDefault();
            return;
        }
        
        if (!aplicarFiltroJalados()){
            event.preventDefault();
            return;
        }

        if (sumaCreditosI < 12) {
            alert('Debe de seleccionar como mínimo 12 créditos en el Periodo I');
            event.preventDefault();
            return;
        }
        
        if (sumaCreditosI > 24) {
            alert('No debe sobrepasar el máximo de 24 créditos en el Periodo I');
            event.preventDefault();
            return;
        }

        if (sumaCreditosII < 12) {
            alert('Debe de seleccionar como mínimo 12 créditos en el Periodo II');
            event.preventDefault();
            return;
        }
        
        if (sumaCreditosII > 24) {
            alert('No debe sobrepasar el máximo de 24 créditos en el Periodo II');
            event.preventDefault();
            return;
        }
    }

    if (!verificarCruceHorarios()) {
        event.preventDefault();
        return;
    }
    
    const mensaje = `Has seleccionado ${cantidadProgramaciones} asignaturas\n¿Estás seguro de que deseas registrar tu matrícula?`;
    if (!window.confirm(mensaje)) {
        event.preventDefault();
    }
}


// Función para obtener el índice de una columna por su nombre TABLA SELECCIONADAS
function obtenerIndiceColumna(nombreColumna) {
    const encabezados = document.querySelectorAll("#tabla_seleccionadas thead th");
    for (let i = 0; i < encabezados.length; i++) {
        if (encabezados[i].textContent.trim() === nombreColumna) {
            return i; // Retorna la posición del encabezado en la tabla
        }
    }
    return -1; // Retorna -1 si no encuentra la columna
}


// Función para verificar cruce de horarios
function verificarCruceHorarios() {
    let horarios = [];
    
    // Obtener índices de las columnas "Días" y "Horas"
    const indiceDias = obtenerIndiceColumna("Días");
    const indiceHoras = obtenerIndiceColumna("Horas");
    const indicePeriodo = obtenerIndiceColumna("Periodo");
    const indiceAsignatura = obtenerIndiceColumna("Nombre");

    if (indiceDias === -1 || indiceHoras === -1) {
        console.error("No se encontraron las columnas 'Días' - 'Horas' - 'Periodo'");
        return false;
    }

    // Obtener todas las filas de la tabla de asignaturas seleccionadas
    const filas = document.querySelectorAll("#tabla_asignaturas_seleccionadas_body tr");

    filas.forEach(fila => {
        let diasTexto = fila.cells[indiceDias].textContent.trim();
        let horasTexto = fila.cells[indiceHoras].textContent.trim();
        let periodo = fila.cells[indicePeriodo].textContent.trim();
        let asignatura = fila.cells[indiceAsignatura].textContent.trim();
        
        // Separar los días y sus respectivos horarios
        let diasArray = diasTexto.split(" | ");
        let horasArray = horasTexto.split(" | ");

        // Crear pares de día y horario
        diasArray.forEach((dia, index) => {
            let [inicio, fin] = horasArray[index].split(" - ");

            // Convertir a objetos de tiempo para facilitar la comparación
            let horaInicio = convertirHora(inicio);
            let horaFin = convertirHora(fin);

            // Almacenar la información estructurada
            horarios.push({ dia, horaInicio, horaFin, periodo, asignatura });
        });
    });

    // Verificar si hay cruces de horarios
    for (let i = 0; i < horarios.length; i++) {
        for (let j = i + 1; j < horarios.length; j++) {
            // Verificar si están en el mismo período y el mismo día
            if (horarios[i].periodo === horarios[j].periodo && horarios[i].dia === horarios[j].dia) {
                // Verificar si los horarios se solapan
                if (horarios[i].horaInicio < horarios[j].horaFin && horarios[i].horaFin > horarios[j].horaInicio) {
                    alert(`Cruce de horario detectado en ${horarios[i].dia} del PERIODO ${horarios[i].periodo}:\n- ${horarios[i].asignatura}\n- ${horarios[j].asignatura}`);
                    return false;
                }
            }
        }
    }
    return true;
}

// Función para convertir hora en formato "HH:MM:SS" a un objeto Date
function convertirHora(horaString) {
    let [horas, minutos, segundos] = horaString.split(":").map(Number);
    return new Date(2000, 0, 1, horas, minutos, segundos); // Usamos una fecha arbitraria
}



// VERIFICACIÓN DE JALADOS
function obtenerVezProgramaciones(tabla){
    const filas = tabla.querySelectorAll("tr");

    // Array para almacenar los datos
    const datosAsignaturas = [];

    filas.forEach(fila => {
        // Obtener las celdas (td) dentro de la fila
        const celdas = fila.querySelectorAll("td");

        // Extraer los valores de las columnas específicas
        const codigo = celdas[2].textContent.trim(); // Código de la asignatura
        const nombreAsignatura = celdas[3].textContent.trim(); // Nombre de la asignatura
        const seccion = celdas[5].textContent.trim(); // Sección de la Asignatura
        const vez = celdas[7].textContent.trim(); // Vez Llevado


        // Guardar los datos en el array
        datosAsignaturas.push({ codigo, nombreAsignatura, seccion, vez});
    });
    return datosAsignaturas;
}


function aplicarFiltroJalados(){
    let vezDisponibles = obtenerVezProgramaciones(document.querySelector(".table-disponibles tbody"));
    let vezSeleccionadas = obtenerVezProgramaciones(document.querySelector(".table-seleccionadas tbody"));

    // Filtrar asignaturas desaprobadas y eliminar duplicados por 'codigo'
    const resultadosDisponibles = vezDisponibles
        .filter((value, index, self) => 
            index === self.findIndex((a) => a.codigo === value.codigo)
        )
        .filter(asignatura => asignatura.vez > 1);

    if (resultadosDisponibles.length === 0){
        return true;
    } else {
        // Comparar si alguna asignatura filtrada está en las seleccionadas
        const coincidencias = resultadosDisponibles.every(item1 => 
            vezSeleccionadas.some(item2 => 
                item1.codigo === item2.codigo
            )
        );
        const noCoinciden = resultadosDisponibles.filter(item1 => 
            !vezSeleccionadas.some(item2 => 
                item1.codigo === item2.codigo
            )
        );
        if (!coincidencias){
            alert(`Debe seleccionar obligatoriamente su/s curso/s desaprobado/s [${noCoinciden.map(item => item.nombreAsignatura).join(", ")}]`);
        }
        return coincidencias;
    }
}

function obtenerVezProgramaciones(tabla) {
    let filas = tabla.querySelectorAll("tr");
    let datos = [];

    filas.forEach(fila => {
        let columnas = fila.querySelectorAll("td");
        if (columnas.length > 0) {
            datos.push({
                periodo: columnas[0].textContent.trim(),  // Extrae el periodo
                codigo: columnas[2].textContent.trim(),  // Extrae el código de la asignatura
                nombreAsignatura: columnas[3].textContent.trim(),
                seccion: columnas[6].textContent.trim(),
                vez: parseInt(columnas[7].textContent.trim(), 10) // Convierte "vez" a número
            });
        }
    });

    return datos;
}

function mayorCuatro() {
    // Obtener datos de la tabla de asignaturas disponibles
    let vezDisponibles = obtenerVezProgramaciones(document.querySelector(".table-disponibles"));

    // Eliminar duplicados por código de asignatura
    const sinDuplicadosDisponible = vezDisponibles.filter((value, index, self) =>
        index === self.findIndex((a) => a.codigo === value.codigo)
    );

    // Filtrar por periodo y vez > 1
    const vezJaladoDisponibleI = sinDuplicadosDisponible.filter(a => a.periodo === 'I' && a.vez > 1);
    const vezJaladoDisponibleII = sinDuplicadosDisponible.filter(a => a.periodo === 'II' && a.vez > 1);

    // Si hay menos de 4 en cada periodo, habilitar filtros
    if (vezJaladoDisponibleI.length < 4 && vezJaladoDisponibleII.length < 4) {
        return true; // Habilitar Filtros
    } else {
        // Obtener datos de la tabla de asignaturas seleccionadas
        let vezSeleccionadas = obtenerVezProgramaciones(document.querySelector(".table-seleccionadas"));

        // Eliminar duplicados por código de asignatura
        const sinDuplicadosSelec = vezSeleccionadas.filter((value, index, self) =>
            index === self.findIndex((a) => a.codigo === value.codigo)
        );

        // Filtrar por periodo y vez > 1
        const vezJaladoSelecI = sinDuplicadosSelec.filter(a => a.periodo === 'I' && a.vez > 1);
        const vezJaladoSelecII = sinDuplicadosSelec.filter(a => a.periodo === 'II' && a.vez > 1);

        console.log("Seleccionadas Periodo I:", vezJaladoSelecI);
        console.log("Seleccionadas Periodo II:", vezJaladoSelecII);

        // Reglas para habilitar/deshabilitar filtros
        if (vezJaladoDisponibleI.length === 0 && vezJaladoDisponibleII.length >= 4) {
            return vezJaladoDisponibleII.length !== vezJaladoSelecII.length;
        } 
        if (vezJaladoDisponibleI.length >= 4 && vezJaladoDisponibleII.length === 0) {
            return vezJaladoDisponibleI.length !== vezJaladoSelecI.length;
        } 
        if (vezJaladoDisponibleI.length >= 4 && vezJaladoDisponibleII.length >= 4) {
            return vezJaladoDisponibleI.length !== vezJaladoSelecI.length || 
                   vezJaladoDisponibleII.length !== vezJaladoSelecII.length;
        }
    }
}
