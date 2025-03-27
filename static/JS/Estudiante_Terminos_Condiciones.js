// Habilitar el botón solo cuando el checkbox esté marcado
const checkbox = document.getElementById('accept_terms');
const submitButton = document.getElementById('submit_button');

checkbox.addEventListener('change', function() {
    submitButton.disabled = !checkbox.checked;
});