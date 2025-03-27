
let shouldWarnOnUnload = true;
let lastHistoryLength = history.length; // Guarda la longitud del historial al inicio

window.addEventListener("popstate", function () {
    if (shouldWarnOnUnload) {
        if (history.length < lastHistoryLength) { 
            // Si history.length disminuye, significa que el usuario fue hacia atrás
            const confirmExit = confirm("¿Seguro que quieres salir? Se perderán los cambios no guardados.");
            if (!confirmExit) {
                history.pushState(null, "", location.href); // Evita salir de la página
            }
        }
    }
    lastHistoryLength = history.length; // Actualiza la referencia del historial
});
