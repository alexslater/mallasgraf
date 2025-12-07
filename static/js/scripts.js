/* SCRIPT.JS

    Este archivo contiene funciones auxiliares en JavaScript para el desarrollo del software 

*/

/* Función que llama al endpoint para eliminar la asignatura de la tabla en vivo */
function eliminarAsignatura(codigo_asignatura, nombre_asignatura) {
    alert('Eliminará la asignatura: ' + codigo_asignatura + ' ' + nombre_asignatura)
    fetch('/comandoeliminar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            codigo_asignatura: codigo_asignatura,
            nombre_asignatura: nombre_asignatura
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect_url) {
            window.location.href = data.redirect_url;  // Redirigir manualmente en el cliente
        }
    })
    .catch(error => console.error('Error:', error));
}

/* Función que llama al endpoint para editar datos de las asignatura */
function editarAsignaturas(codigo_asignatura, nombre_asignatura) {
    fetch('/comandoeditar', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            codigo_asignatura: codigo_asignatura,
            nombre_asignatura: nombre_asignatura
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.redirect_url) {
            window.location.href = data.redirect_url;  // Redirigir manualmente en el cliente
        }
    })
    .catch(error => console.error('Error:', error));
}