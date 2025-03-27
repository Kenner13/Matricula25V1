let minutos = 15;
let segundos = 0;

function cargarSegundo(){
    let txtSegundos;
    if (segundos < 0){
        segundos = 59;
    }

    if (segundos < 10){
        txtSegundos = `0${segundos}`;
    } else {
        txtSegundos = segundos;
    }

    document.getElementById('segundos').innerHTML = txtSegundos;
    segundos--;
    cargarMinutos(segundos);
}

function cargarMinutos(segundos){
    let txtMinutos;
    if (segundos == -1 && minutos !== 0){
        setTimeout(() => {
            minutos--;
        }, 500)
    } else if (segundos == -1 && minutos == 0){
        alert('Se agotó el tiempo de selección de cursos, la selección de cursos de reiniciará.')
        shouldWarnOnUnload = false;
        location.reload();
    }

    if (minutos < 10){
        txtMinutos = `0${minutos}`;
    } else {
        txtMinutos = minutos;
    }
    document.getElementById('minutos').innerHTML = txtMinutos;

}

setInterval(cargarSegundo, 1000);