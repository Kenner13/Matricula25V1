function alertaGuardar(event) {
    // Obtener los valores de los campos
    let diaApertura = document.querySelector('input[name="D_DiaApertura"]').value;
    let horaApertura = document.querySelector('input[name="D_HoraApertura"]').value;
    let diaCierre = document.querySelector('input[name="D_DiaCierre"]').value;
    let horaCierre = document.querySelector('input[name="D_HoraCierre"]').value;
    let categoria = document.querySelector('select[name="T_Categoria"]').value;
    let clave = document.querySelector('input[name="contrasena"]').value

    // Validar que los campos no estén vacíos
    if (!diaApertura || !horaApertura || !diaCierre || !horaCierre || !categoria) {
        alert("Por favor, complete todos los campos antes de guardar.");
        return;  // IMPORTANTE: Se debe detener la ejecución aquí
    }

    if (!cruceHorarios(horaApertura, horaCierre, diaApertura, diaCierre)) {
        return;  // Evita seguir si hay un error en los horarios
    }

    // Mensaje de confirmación si todo está correcto
    if (clave === '123456')
        alert("Se guardaron los datos del acceso de matrícula seleccionada");
    else
        alert("La clave ingresada es INCORRECTA");
}

function cruceHorarios(horaApertura, horaCierre, diaApertura, diaCierre) {
    let horaInicio = convertirHora(horaApertura);
    let horaFin = convertirHora(horaCierre);

    // Verificar si hay cruces de horarios en el mismo día
    if (diaApertura === diaCierre) {
        if (horaInicio >= horaFin) {
            alert("La hora de Apertura no puede ser mayor o igual a la hora de Cierre");
            return false;
        }
    }

    return true;  // Retornar `true` cuando no hay problemas
}

function convertirHora(horaString) {
    let [horas, minutos, segundos] = horaString.split(":").map(Number);
    return horas * 60 + minutos; // Convertimos a minutos totales para facilitar comparación
}
