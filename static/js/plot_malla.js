const areas = [{'codigo':'ba', 'nombre':'Básica'}, 
    {'codigo':'es', 'nombre':'Específica'},
    {'codigo':'el', 'nombre':'Electiva'}]

let datos_malla = [];

let id_asignatura_agregada = 0
let tabla_asignaturas = []
let datos_asignatura = {}
let agregada = false

/* esta funcion crea la tabla matriz */
async function crear_matriz() {

    let tr = "";
    let td = "";
    let th = "";
    let codigo_celda = "";
    
    // Limpiar matriz
    document.getElementById("tabla-malla").innerHTML = 
    `
                <thead id="malla-header">
   
                </thead>
    
                <tbody id="malla-body">
                  
                </tbody>
    `
    // Semestres
    tr = document.createElement("tr")
    for(let i = 1; i < datos_malla.numero_semestres+1; i++){
        th = document.createElement("th")
        th.setAttribute("class","semestre-tamano")
        th.innerHTML = 
        `
            <div class="sem-celda fs-6 titulo-semestre text-white">
            Nivel ${i}
            </div>
        `
        tr.appendChild(th)
    }
    document.getElementById("malla-header").appendChild(tr)


    /* Determinar el número de asignaturas máximas por área */
    const max_asig_basica = datos_malla.max_total_asignaturas_por_area[0].max_total_asignaturas
    const max_asig_electiva = datos_malla.max_total_asignaturas_por_area[1].max_total_asignaturas
    const max_asig_especifica = datos_malla.max_total_asignaturas_por_area[2].max_total_asignaturas

    // Area específica
    for(let i = 1; i < max_asig_especifica+1; i++) {
        tr = document.createElement("tr")
        //tr.className = "area-especifica"
        for(let j = 1; j < datos_malla.numero_semestres+1; j++) {
            td = document.createElement("td")
            td.className = "card-tamano"
            codigo_celda = "es-"+ i + "-" + j 
            td.setAttribute("id", codigo_celda)
            td.innerHTML = ""
            tr.appendChild(td)
        }
        document.getElementById("malla-body").appendChild(tr)
    }

    //Area basica
    for(let i = 1; i < max_asig_basica+1; i++) {
        tr = document.createElement("tr")
        //tr.className = "area-basica"
        for(let j = 1; j < datos_malla.numero_semestres+1; j++) {
            td = document.createElement("td")
            td.className = "card-tamano"
            codigo_celda = "ba-" + i + "-" + j 
            td.setAttribute("id", codigo_celda)
            td.innerHTML = ""
            tr.appendChild(td)
        }
        document.getElementById("malla-body").appendChild(tr)
    }

    //Area electiva
    for(let i = 1; i < max_asig_electiva+1; i++) {
        tr = document.createElement("tr")
        //  tr.className = "area-electiva"
        for(let j = 1; j < datos_malla.numero_semestres+1; j++) {
            td = document.createElement("td")
            td.className = "card-tamano"
            codigo_celda = "el-" + i + "-" + j 
            td.setAttribute("id", codigo_celda)
            td.innerHTML = ""
            tr.appendChild(td)
        }
        document.getElementById("malla-body").appendChild(tr)
    }
}

function escribe_asignaturas() {
    const plan_estudios = datos_malla.data;

    for(const asig of plan_estudios) {
        console.log("PROCESO ASIGNATURA")
        console.log(asig.id)
        console.log(asig.Asignatura)
        console.log(asig.Tipo)
        document.getElementById(asig.id).innerHTML =
        `<div class="data-celda fs-6 text-white area-${asig.Tipo}">
        ${asig.Asignatura}
        </div>
        `
        //document.getElementById(asig.id).setAttribute("class", "area-"+asig.Area+" data-celda text-white")
    }
   
}

function guardarInformacionMalla() {
    localStorage.clear();
    let arreglo_estudiantes = []
    for(const e of estudiantes)
        arreglo_estudiantes.push(e);
    localStorage.setItem("estudiantes", JSON.stringify(arreglo_estudiantes));

}

function recuperarInformacionMalla() {
    datos_malla = JSON.parse(localStorage.getItem("malla"))
    console.log(datos_malla)
    crear_matriz()
    escribe_asignaturas()
}

/* en esta funcion habria que usasr un fetch a la API para ejecutar un request con
la payload de un nuevo HTML generado */

async function generarPDF() {

    // Hasta aqui declarar la primera parte del header
    let html_payload =
    `
    <!DOCTYPE html>
    <html lang="es">
    <head>
        <meta charset="UTF-8">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <meta name="viewport" content="width-device-width, initial-scale=1.0">
        <meta name="description" content="Sitio de pruebas para graficar mallas curriculares">
        <meta name="keywords" content="CURSOS ELECTVOS UNIVERSIDAD PROYECTOS APRENDIZAJE CERTIFICACIONES CURRICULUM">

        <!-- Fuentes de google para el proyecto -->
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Lato:ital,wght@0,400;0,700;0,900;1,400&display=swap" rel="stylesheet">
    </head>

    <body class="" style="">
        <header>

        </header>

        <main class="container-lg">

            <div class="container-lg" id="malla">
            <table id="tabla-malla">

    `
    const tabla = document.getElementById("tabla-malla").innerHTML

    // agregamos esto
    html_payload = html_payload + tabla

    let html_payload_end = 
    `
        </table>

        </div>

        </main>

        <footer> </footer>
    
    </body>
    </html>


    `

    html_payload = html_payload + html_payload_end
    
    //testeo por consola
    console.log(html_payload)


    // AGREGAR PROMESA
    // Realizar el request a la API para armar el PDF
    try {
        URL = "http://tredu.hopto.org:5000/generarpdf"
        URL_local = "http://127.0.0.1:5000/generarpdf"
        response = await fetch(URL_local, {
            method: "POST",
            body: JSON.stringify({
            "data_html": html_payload,
            }),
            headers: {
            "Content-type": "application/json; charset=UTF-8",
            }
        })
        json = await response.json()
        alert(json)
    } catch (err) {
        alert(err);
    }

}

async function subir() {

    const fileInput = document.getElementById('fileInput');
    const endpoint_public = "http://tredu.hopto.org:5000/upload"
    const endpoint = 'http://127.0.0.1:5000/upload';
    const file = fileInput.files[0];
    const formData = new FormData();
    //let response = "";
    //let json = "";
    formData.append('file', file);
    try {
        const response = await fetch(endpoint, {method: 'POST', body: formData});
        const json = await response.json();

        // Guardar datos de la malla en localStorage
        localStorage.clear()
        localStorage.setItem("malla", JSON.stringify(json))

        alert("Archivo cargado y procesado correctamente en el servidor.")
        localStorage.setItem("malla_cargada", true);
    }
    catch(err) {
            console.error(err)
            alert(err)
            alert('Error al cargar el archivo en el servidor.')
    }

}

/* Habilitar modal de ingreso de asignaturas */
function montarModalAsignatura() {

    // Limpiar parte interna del modal
    document.getElementById("formulario-entrada").innerHTML = ""

    const div_form = document.createElement("div")
    div_form.setAttribute("id", "form-asignatura")

    div_form.innerHTML =
    `
        <div class="form-group row">
            <div class="form-group col-md-6">
                <label for="nivel-asignatura">Nivel</label>
                <select class="form-control" name="nivel-asignatura" id="nivel-asignatura">
                    
                </select>
            </div>
            <div class="form-group col-md-6">
                <label for="area-asignatura">Área</label>
                <select class="form-control" name="area-asignatura" id="area-asignatura">
                    
                </select>
            </div>
        </div>
        <div class="form-row">
            <div class="form-group col-md-6">
                <label for="nombre-asignatura">Nombre de asignatura</label>
                <input class="form-control" type="text" id="nombre-asignatura" onchange="nombretoUpper()">
            </div>
        </div>
    `

    // Montar botones por defecto
    document.getElementById("botones-modal").innerHTML = 
    `
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="cerrarMalla">Cancelar</button>
        <button type="button" class="btn btn-primary" data-bs-dismiss="modal" id="agregarAsignatura">Agregar</button>
    `
   
    document.getElementById("formulario-entrada").appendChild(div_form)

    // Cargar niveles de malla
    const modalbody_nivel = document.getElementById("nivel-asignatura")
    for(let i = 1; i < 15; i++){
        const opcion = document.createElement("option")
        opcion.setAttribute("value", i.toString())
        opcion.innerHTML = i.toString()
        modalbody_nivel.appendChild(opcion)
    }

    // Cargar opciones de area
    const modalbody_area = document.getElementById("area-asignatura")
    for(const a of areas) {
        const area = document.createElement("option")
        area.setAttribute("value", a.codigo)
        area.innerHTML = a.nombre
        modalbody_area.appendChild(area)
    }
   
}


/* Esta funcion crea asignatura, asigna código y monta llama al montaje del
modal de la asignatura */
function crearAsignatura () {
    // limpiar datos antes de seguir
    datos_asignatura = {} 
    asignaturas_agregadas = asignaturas_agregadas + 1
    montarModalAsignatura()
    const agregarAsignatura = document.getElementById('agregarAsignatura')
    agregarAsignatura.addEventListener('click', agregarNuevaAsignatura)
}

/* Convierte el nombre de asignatura a mayusculas cuando el usuario termina de ingresar en el campo de entrada */
function nombretoUpper() {
    const texto = document.getElementById("nombre-asignatura").value
    document.getElementById("nombre-asignatura").value = texto.toUpperCase()
    console.log("nombre to upper")
}


/* Limpia el canvas donde se almacenan las asignaturas */
function limpiarAsignaturas() {
    asignaturas_agregadas = 0
    document.getElementById("malla").innerHTML = ""
    document.getElementById("malla").innerHTML = 
    `
        
        <div class="container margenes-barra" id="barra-botones-asignatura">
                <div class="row">
                    <div class="col-md-2">
                        <button class="btn btn-primary" data-bs-toggle="modal" data-bs-target="#crearMallaModal" href="#" id="nuevaAsignatura">Nueva Asignatura</button> 
                    </div>
                </div>
            </div>
        <div class="container" id="filas-asignaturas">

        </div>
            
    `
    const nuevaAsignatura = document.getElementById('nuevaAsignatura')
    nuevaAsignatura.addEventListener('click', crearAsignatura)
}

/* Elimina asignatura de la tabla HTML y del registro de datos */
function eliminarAsignatura() {
    
    let id_boton_click = event.srcElement.id;
    console.log("BOTON ELIMINAR = " + id_boton_click)

    alert("Eliminará la asignatura: " + id_boton_click)
    const id_datos = id_boton_click.split("-")[3]
    document.getElementById("tr-asignatura-n-"+id_datos).remove()

    // Realiza la actualización de la tabla de datos.
    tabla_asignaturas = removerElementoArray(tabla_asignaturas, id_datos)


}

function removerElementoArray(tbl, id_elemento) {

    let nueva_tabla = []
    for(const a of tbl) {
        if(a.id_asignatura != id_elemento)
            nueva_tabla.push(a)
    }
    return nueva_tabla

}

function agregarNuevaAsignatura() {

    console.log("nombre asignatura ingresado: "+ document.getElementById('nombre-asignatura').value)

    let area = ""
    if(document.getElementById('area-asignatura').value === 'ba') area = 'Básica'
    if(document.getElementById('area-asignatura').value === 'es') area = 'Específica'
    if(document.getElementById('area-asignatura').value === 'el') area = 'Electiva'

    datos_asignatura = {
        'id_asignatura': id_asignatura_agregada,
        'nivel': document.getElementById('nivel-asignatura').value, 
        'area': document.getElementById('area-asignatura').value,
        'nombre_area': area,
        'nombre_asignatura': document.getElementById('nombre-asignatura').value
    }
    tabla_asignaturas.push(datos_asignatura)
    //Actualizar el id
    id_asignatura_agregada = id_asignatura_agregada + 1
    // Renderizar
    renderizarTablaAsignaturas()

}

/* Funcion que renderiza la tabla de asignaturas cada vez que 
   que se ingresa una nueva a través del modal */
function renderizarTablaAsignaturas() {

    const filas_asignaturas = document.getElementById("filas-asignaturas")
    filas_asignaturas.innerHTML = ""
    filas_asignaturas.innerHTML = 
    `
    <table class="table" data-toggle="table" data-sortable="true">
        <thead>
            <th scope="col">ID</th>
            <th scope="col" data-sortable="true" data-field="nivel">Nivel</th>
            <th scope="col" data-sortable="true" data-field="area">Area</th>
            <th scope="col">Nombre asignatura</th> 
            <th scope="col">Accion</th>
        </thead>
        <tbody id="tabla-asignaturas">

        </tbody>
    </table>
    `
    
    // Recorrer datos de arreglo e insertar

    const tbody = document.getElementById("tabla-asignaturas")


    for(const asig of tabla_asignaturas) {
        const tr = document.createElement("tr")
        tr.setAttribute("id", "tr-asignatura-n-"+asig.id_asignatura)
  
            
        tr.innerHTML = 
        `
            <td>${asig.id_asignatura}</td>
            <td>${asig.nivel}</td>
            <td>${asig.nombre_area}</td>
            <td>${asig.nombre_asignatura}</td>
            <td>
                <button class="btn btn-danger" id="btn-eliminar-asig-${asig.id_asignatura}" onclick=eliminarAsignatura()>Eliminar</button>
                <button type="button" class="btn btn-secondary" data-bs-toggle="modal" data-bs-target="#crearMallaModal" onClick="editarAsignatura()" id="btn-editar-asig-${asig.id_asignatura}">Editar</button>
            </td> 

        `
        tbody.appendChild(tr)        
    }


}

function nombreArea(id_area) {

    let area = ""
    if(id_area === 'ba') area = 'Básica'
    if(id_area === 'es') area = 'Específica'
    if(id_area === 'el') area = 'Electiva'

    return area
}


/* Busca una asignatura en la tabla y devuelve el objeto con los datos */
function buscarAsignatura(id_asignatura) {

    for(const a of tabla_asignaturas) {
        if(a.id_asignatura == id_asignatura){
            console.log(">>>BUSCAR ASIGNATURA")
            console.log(a)
            return a
        }
    }

}

/* Función que llama a modal y permite la edición de datos de asignatura */
function editarAsignatura() {

    // Revisar id boton presionado y montar modal
    let id_boton_click = event.srcElement.id;
    console.log("BOTON ELIMINAR = " + id_boton_click)
    const id_datos = id_boton_click.split("-")[3]
    montarModalAsignatura()

    // Agregar botones del modal
    document.getElementById("botones-modal").innerHTML = 
    `
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal" id="cerrarMalla">Cancelar</button>
        <button type="button" class="btn btn-primary" data-bs-dismiss="modal" id="guardarCambios-n-${id_datos}">Guardar cambios</button>
    `
    
    const btn_modal_guardarCambio = document.getElementById("guardarCambios-n-"+id_datos)
    btn_modal_guardarCambio.addEventListener("click", guardarCambios)

    //cargar datos de la asignatura en modal
    let datos_actuales_asignatura = buscarAsignatura(id_datos)
    document.getElementById("nivel-asignatura").value = datos_actuales_asignatura.nivel
    document.getElementById("area-asignatura").value = datos_actuales_asignatura.area
    document.getElementById("nombre-asignatura").value = datos_actuales_asignatura.nombre_asignatura
    
}

function guardarCambios() {

    let id_boton_click = event.srcElement.id;
    const id_datos = id_boton_click.split("-")[2]

    tabla_asignaturas = removerElementoArray(tabla_asignaturas, id_datos)
   
    console.log("Esta guardando cambios!")
    let nuevos_datos_asig = {}
    nuevos_datos_asig = {
        "id_asignatura": id_datos,
        "nivel":  document.getElementById("nivel-asignatura").value,
        "area": document.getElementById("area-asignatura").value,
        "nombre_area": nombreArea(document.getElementById("area-asignatura").value),
        "nombre_asignatura": document.getElementById("nombre-asignatura").value
    }

    tabla_asignaturas.push(nuevos_datos_asig)
    renderizarTablaAsignaturas()
    
}


function main(){
    
    // Evento click de carga
    const uploadButton = document.getElementById('uploadButton');
    uploadButton.addEventListener('click', subir)

    //Evento para recuperar datos de localStorage
    const recuperarMalla = document.getElementById('recuperarMalla')
    recuperarMalla.addEventListener('click', recuperarInformacionMalla)

    //Evento para generar malla PDF
    const generarPDFMalla = document.getElementById('generarPDFMalla')
    generarPDFMalla.addEventListener('click', generarPDF)

    //Evento para agregar asignatura

    //Evento inicio de creación de nueva mallas
    const crearAsignaturas = document.getElementById('crearAsignaturas')
    crearAsignaturas.addEventListener('click', limpiarAsignaturas)

    // Evento para boton de nueva asignatura


}


main()



    