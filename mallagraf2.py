from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_from_directory
from forms import XLSForm, EditarForm
from werkzeug.utils import secure_filename
import os
from xls2json import XLSConverter
import uuid
import sqlite3
import json
from weasyprint import HTML, CSS
from datetime import datetime
from PlanEstudios import PlanEstudios


datos_malla = {}
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'xls', 'xlsx'}

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

lista_asignaturas = []
datos_asignaturas = {}

app = Flask(__name__)
app.config['SECRET_KEY'] = 'mysecret'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route("/", methods=['GET','POST'])
def index():
    return render_template("base.html")


@app.route("/crearasignatura", methods=['GET', 'POST'])
def crearasignatura():
    xls_form = XLSForm(csrf_enabled=False)
    
    # Validar si formulario se ha completado
    if xls_form.validate_on_submit():
        nombre_asignatura = xls_form.nombre_asignatura.data.upper()
        codigo_asignatura = xls_form.codigo_asignatura.data.upper()
        datos_asignaturas[codigo_asignatura] = nombre_asignatura
        print(f"DEBUG> datos_asignaturas = {datos_asignaturas}")
        return redirect(url_for('displaymalla', codigo_asignatura=codigo_asignatura )) # se quita _external=True, _scheme='https' para desarrollo con debug
    return render_template("cargarxls.html", template_form=xls_form)


@app.route("/cargarxls", methods=['GET', 'POST'])
def cargarxls():
    xls_form = XLSForm(csrf_enabled=False)
    if xls_form.validate_on_submit():
        if request.method == 'POST':
            if 'archivo_xlsx' not in request.files:
                flash('No existe archivo para cargar')
                print(f"DEBUG>No se encuentra File en request")
                return redirect(url_for('renderizamalla'))
            file = request.files['archivo_xlsx']
            if file.filename == '':
                flash("NO hay archivo seleccionado")
                print(f"DEBUG> No hay archivo correcto")
                return redirect(url_for('renderizamalla'))
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                ext = filename.rsplit('.', 1)[1].lower()  # Obtiene la extensión del archivo
                new_filename = f"{uuid.uuid4().hex}"  # Genera un nombre aleatorio con la misma extensión    
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_filename))
                print(f"DEBUG> Carga de archivo XLSX: {file.filename},  nombre seguro = {new_filename}")
                return redirect(url_for('guardarmallaBD', filename=new_filename, nombre_carrera=xls_form.nombre_carrera.data))        
    return render_template("cargarxls.html", template_form=xls_form)


@app.route("/guardarmallaBD/<filename>/<nombre_carrera>")
def guardarmallaBD(filename, nombre_carrera):
    xlsconverter = XLSConverter()
    datos_malla = xlsconverter.procesaExcel("./uploads/", filename)

    #Guardar los datos recibidos en BD SQL
    conn = sqlite3.connect("mallas.db")
    cursor = conn.cursor()

    #Crear tabla si no existe
    cursor.execute(''' CREATE TABLE IF NOT EXISTS mallas (
                   idmalla varchar(100),
                   nombre_carrera varchar(50),
                   jsonpayload text,
                   fecha_creacion text)''')
    conn.commit()

    timestamp = datetime.now().isoformat(sep=' ', timespec='seconds')

    #Insertar registro
    datos_malla['carrera'] = nombre_carrera
    cursor.execute(f"""INSERT INTO mallas VALUES ('{filename}', '{nombre_carrera}', '{json.dumps(datos_malla)}', '{timestamp}') """)
    conn.commit()

    #result=cursor.execute("SELECT * FROM mallas")
    #return redirect(url_for('renderizamalla', idmalla=filename))
    return render_template("tablamallas.html", listaasignaturas=datos_malla['data'], filename=filename, nombre_carrera=nombre_carrera)


# Hay que modificar el renderizamalla para que lea los datos desde la base de datos
# local SQL que tiene ya cargados, los datos desde guardar malla.


@app.route("/renderizamalla/<filename>/<nombre_carrera>")
def renderizamalla(filename, nombre_carrera):

    # Acá se debe modificar para que en lugar de leer el XLSX cargado,
    # haga la laamada a la base de datos

    #xlsconverter = XLSConverter()
    #datos_malla = xlsconverter.procesaExcel("./uploads/", filename)

    print(f"DEBUG renderizamalla> Nombre de archivo pasado {filename}")
    print(f"DEBUG renderizamalla> Nombre de carrera pasado {nombre_carrera}")

    # Se agrega datos para la conexión a una base de datos SQLITE3
    conn = sqlite3.connect("mallas.db")
    cursor = conn.cursor()
    result = cursor.execute(f"SELECT * FROM mallas WHERE idmalla = '{filename}'")
    for row in result:
        datos_malla = json.loads(row[2])

    #Creamos objeto plan de estudios
    pe = PlanEstudios(datos_malla)

    #usar este print para recuperar datos...
    #print(f"DEBUG renderizamalla V2> {datos_malla}")
    numero_semestres = datos_malla['numero_semestres']
    max_asig_por_area = datos_malla["max_total_asignaturas_por_area"]
   
    #incorporamos cálculos para el tamaño de página PDF
    ancho_px = (numero_semestres + 1) * 120 + 200  # +1 por columna lateral de áreas, +200 px para márgenes
    alto_px = sum(area["max_total_asignaturas"] for area in max_asig_por_area) * 40 + 400  # filas por altura + título + espacio extra
    css_dinamico = generar_css_dinamico(ancho_px, alto_px)



    html = """
    <table id="tabla-malla">
        <thead id="malla-header">
            <tr><th colspan="{}" class="cabecera-malla">"""+nombre_carrera.upper()+"""</th></tr>
        </thead>
        <tbody id="malla-body">
            <tr>
                <td class="semestre-tamano"></td>
    """.format(numero_semestres + 1)
    
    for i in range(1, numero_semestres + 1):
        html += f'<td class="semestre-tamano"><div class="sem-celda fs-6 titulo-semestre text-white">Nivel {i}</div></td>'
    
    html += "</tr>"
    
    areas = ['Disciplinar', 'Básica', 'Electiva']
    area_classes = ['area-es', 'area-ba', 'area-el']
    
    #Acá se preparan los cuadros de áreas específica, básica y electiva
    #esto se ocupaba en javascript para calcular el tamaño del cuadro
    #const px_ba = ((max_asig_basica+1)*120) - ((max_asig_basica+1)*20)

    for idx, area in enumerate(areas):
        max_asig = max_asig_por_area[idx]["max_total_asignaturas"]
        max_asig_area = pe.getNoAsignaturasporArea(area)
        px_ba = ((max_asig_area+1)*115) - ((max_asig_area+1)*15)
        #style="height: {px_ba}px"
        html += f'''<tr><td rowspan="{max_asig + 1}">
                <div class="titulo-vertical-celda fs-6 text-white {area_classes[idx]}" style="height: {px_ba}px">
                    {area}
                </div>
        </td></tr>'''
        
        for i in range(1, max_asig + 1):
            html += "<tr>"
            for j in range(1, numero_semestres + 1):
                idasig = f'{area_classes[idx].split("-")[1]}-{i}-{j}'
                html += f'''<td class="card-tamano" id="{area_classes[idx].split("-")[1]}-{i}-{j}">
                    <div class="data-celda fs-6 text-white area-{pe.getTipo(idasig)}">
                        <table>
                            <tr>
                                <td class="data-prerequisito">{pe.getN(idasig)}</td>
                            </tr>
                            <tr>
                                <td class="data-nombre-asignatura">{pe.getAsignatura(idasig)}</td>
                            </tr>
                            <tr>
                                <td class="data-prerequisito">{pe.getPrerequisito(idasig)}</td>
                                <td class="data-sct">{pe.getSCT(idasig)} SCT</td>
                            </tr>
                        </table>
                    </div>
                </td>'''
            html += "</tr>"
    
    html += "</tbody></table>"
    

    html_payload = """
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

    """
    html_payload_end = """
     </div>

        </main>

        <footer> </footer>
    
    </body>
    </html>

    """
    

    html_txt = html_payload + html + html_payload_end
    #Guardar el código HTML generado en carpeta temporal
    f = open(f"./html_render/{filename}.html", "w")
    f.writelines(html_txt+"\n")
    f.close()
    #os.system(f"wkhtmltoimage --format svg --user-style-sheet ./static/css/style_print.css ./html_render/{filename}.html ./svg/{filename}.svg")
    #os.system(f"svg2pdf ./svg/{filename}.svg ./pdf/{filename}.pdf")
    css_path = os.path.join('static', 'css', 'style.css')
    html_rendered = render_template("rendermalla.html", html=html, filename=filename)
    pdf = HTML(string=html_txt, base_url=request.base_url).write_pdf(f"./pdf/{filename}.pdf", stylesheets=[CSS("./static/css/style_print.css")])
    
    return render_template("rendermalla.html", html=html, filename=filename)

@app.route("/editarTablaAsignaturas/<filename>", methods=['GET', 'POST'])
def editarTablaAsignaturas(filename):
    conn = sqlite3.connect("mallas.db")
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM mallas WHERE idmalla = ?", (filename,))
    row = result.fetchone()
    if row is None:
        flash("No se encontró la malla con el ID proporcionado.")
        return redirect(url_for('listarmallas'))    
    datos_malla = json.loads(row[2])
    return render_template("tablamallas.html", listaasignaturas=datos_malla['data'], filename=filename, nombre_carrera="TEST")

######################################################################
#                                                                    #
# editarAsignatura                                                   #
#                                                                    #                                 
# Aca agregaremos ruta para editar una asignatura que está en tabla  #
# Deberíamos devolver el formulario y luego cargar en la base de     #
# datos el cambio realizado.                                         #
######################################################################

@app.route("/editarAsignatura/<filename>/<codigo_asignatura>", methods=['GET', 'POST'])
def editarAsignatura(filename, codigo_asignatura):
    conn = sqlite3.connect("mallas.db")
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM mallas WHERE idmalla = ?", (filename,))
    row = result.fetchone()
    if row is None:
        flash("No se encontró la malla con el ID proporcionado.")
        return redirect(url_for('listarmallas'))   
     
    datos_malla = json.loads(row[2])

    #Creamos objeto plan de estudios
    pe = PlanEstudios(datos_malla)

    #Buscar la asignatura en los datos de la malla
    codigo_ubicacion = pe.getCodigoUbicacion(codigo_asignatura)
    
    #datos de la malla

    nombre_asignatura = pe.getAsignatura(codigo_ubicacion)
    nivel = pe.getNivel(codigo_ubicacion)
    area = pe.getNombreArea(codigo_ubicacion)
    sct = pe.getSCT(codigo_ubicacion)
    

    editar_form = EditarForm(
        data={
        'codigo_asignatura': codigo_asignatura,
        'nombre_asignatura': nombre_asignatura,
        'nivel': nivel,
        'area': area,
        'sct': sct,
        'codigo_ubicacion': codigo_ubicacion
        }
    )

    # Validar envio del formulario
    if request.method == 'POST' and editar_form.validate_on_submit():
        # Aquí puedes acceder a cada campo con .data
        codigo = editar_form.codigo_asignatura.data
        nombre = editar_form.nombre_asignatura.data
        nivel = editar_form.nivel.data
        area = editar_form.area.data
        sct = editar_form.sct.data
        codigo_ubicacion = editar_form.codigo_ubicacion.data

        # Procesar los datos (por ejemplo, actualizar en la BD)
        # Aca mismo hay que actualizar....
        pe.updateAsignatura(codigo, asignatura=nombre, nivel=nivel, area=area, sct=sct)
        print(f"DEBUG editarAsignatura> {area}")
        try:
            cursor.execute("UPDATE mallas SET jsonpayload = ? WHERE idmalla = ?", (json.dumps(pe.getPEJSON()), filename))
            conn.commit()
        except sqlite3.Error as e:
            print(f"DEBUG> Error al actualizar la asignatura: {e}")
            flash("Error al actualizar la asignatura", "error")
            return

        # Confirmación y redirección
        #flash("Asignatura actualizada exitosamente.", "success")
        return redirect(url_for("renderizamalla", filename=filename, nombre_carrera="editado"))  # o donde desees redirigir
    
    return render_template("editarasignatura.html", template_form=editar_form, 
                           codigo_asignatura=codigo_asignatura, nombre_asignatura=nombre_asignatura, 
                           nivel=nivel, area=area, sct=sct, codigo_ubicacion=codigo_ubicacion)



def actualizar_asignatura(codigo, nombre, nivel, area, sct):
    #conexion a la base de datos
    conn = sqlite3.connect("mallas.db")
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM mallas")
    #Aquí deberías buscar y actualizar la asignatura en la base de datos
    rows = result.fetchall()
    for row in rows:
        datos_malla = json.loads(row[2])
        for asignatura in datos_malla['data']:
            if asignatura['ID Asignatura'] == int(codigo):
                asignatura['Asignatura'] = nombre
                asignatura['Nivel'] = nivel
                asignatura['Area'] = area
                asignatura['SCT'] = sct
                print(f"DEBUG> Asignatura actualizada en memoria: {asignatura}")
                #Actualizar el registro en la base de datos
                try:
                    cursor.execute("UPDATE mallas SET jsonpayload = ? WHERE idmalla = ?", (json.dumps(datos_malla), row[0]))
                    conn.commit()
                except sqlite3.Error as e:
                    print(f"DEBUG> Error al actualizar la asignatura: {e}")
                    flash("Error al actualizar la asignatura", "error")
                    return
                print(f"DEBUG> Registro de malla {row[0]} actualizado en la base de datos.")
                break

    print(f"DEBUG actualizar_asignatura> Actualizando asignatura: {codigo}, {nombre}, {nivel}, {area}, {sct}")
    flash(f"Asignatura {codigo} actualizada correctamente", "success")
    return

#
# crearAsignatura
#  
# Esta función debe permitir la creación de una nueva asignatura
# y agregarla a la malla correspondiente.
#
@app.route("/crearAsignatura/<filename>", methods=['GET', 'POST'])
def crearAsignatura(filename):
    crear_form = EditarForm()
    if request.method == 'POST' and crear_form.validate_on_submit():
        codigo = crear_form.codigo_asignatura.data
        nombre = crear_form.nombre_asignatura.data
        nivel = crear_form.nivel.data
        area = crear_form.area.data
        sct = crear_form.sct.data

        # Procesar los datos (por ejemplo, insertar en la BD)
        #insertar_asignatura(filename, codigo, nombre, nivel, area, sct)

        # Confirmación y redirección
        flash("Asignatura creada exitosamente.", "success")
        return redirect(url_for("editarTablaAsignaturas", filename=filename))  # o donde desees redirigir
    
    return render_template("crearasignatura.html", template_form=crear_form)


def generar_css_dinamico(ancho_px, alto_px):
    return f"""
   <style>
    @page {{
        size: auto auto;
        margin: 0;
    }}

    html, body {{
        width: auto;
        height: auto;
        margin: 0;
        padding: 0;
        overflow: auto;
        font-family: Arial, sans-serif;
    }}

    table {{
        border-collapse: collapse;
        width: 100%;
    }}

    td, th {{
        padding: 5px;
        text-align: center;
        font-size: 12px;
    }}

    tr, td {{
        page-break-inside: avoid !important;
    }}
    </style>
    """

@app.route("/generarPDFMalla/<filename>", methods=['GET', 'POST'])
def generarPDFMalla(filename):
    return render_template("generarPDF.html", filename=filename)


@app.route("/descargaPDFMalla/<filename>", methods=['GET', 'POST'])
def descargaPDFMalla(filename):
    return send_from_directory('pdf', filename+".pdf", as_attachment=True)

@app.route("/quehay")
def quehay():
    #Guardar los datos recibidos en BD SQL
    conn = sqlite3.connect("mallas.db")
    cursor = conn.cursor()
    result=cursor.execute("SELECT * FROM mallas")
    r = {}
    for row in result:
        r[row[0]] = json.loads(row[1])
    #return redirect(url_for('renderizamalla', idmalla=filename))
    return render_template("test.html", datosmallas=r)

@app.route("/displaymalla/<codigo_asignatura>")
def displaymalla(codigo_asignatura):
    return render_template("displaymalla.html", codigo_asignatura=codigo_asignatura, nombre_asignatura=datos_asignaturas[codigo_asignatura])

@app.route("/listarmallas")
def listarmallas():
    #Recuperar datos de la base de datos
    conn = sqlite3.connect("mallas.db")
    cursor = conn.cursor()
    result = cursor.execute("SELECT * FROM mallas")
    lista_mallas = []
    for row in result:
        malla = {
            'idmalla': row[0],
            'nombre_carrera': row[1],
            'jsonpayload': json.loads(row[2]),
            'fecha_creacion': row[3]
        }
        lista_mallas.append(malla)
    return render_template("listarmallas.html", lista_mallas=lista_mallas)

@app.route("/eliminarmalla/<idmalla>")
def eliminarmalla(idmalla):
    # Aquí podrías implementar la lógica para eliminar una malla de la base de datos
    # Por ahora, solo se muestra un mensaje de éxito
    conn = sqlite3.connect("mallas.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM mallas WHERE idmalla = ?", (idmalla,))
    conn.commit() 
    # Eliminar el archivo asociado a la malla
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], idmalla)
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"DEBUG> Archivo {file_path} eliminado correctamente")
    else:
        print(f"DEBUG> Archivo {file_path} no encontrado, no se puede eliminar")

    flash("Malla eliminada correctamente")

    return redirect(url_for('listarmallas'))  

@app.route("/eliminarasignatura/<codigo_asignatura>/<nombre_asignatura>")
def eliminarasignatura(codigo_asignatura, nombre_asignatura):
    msg = f"Se ha eliminado la asignatura {codigo_asignatura} {nombre_asignatura}"
    flash(msg)
    return redirect(url_for('index'))
    
@app.route('/comandoeditar', methods=['POST'])
def comandoeditar():
    data = request.get_json()  # Recibe el ID del producto desde el frontend
    codigo_asignatura = data.get('codigo_asignatura')
    nombre_asignatura = data.get('nombre_asignatura')
    # Aquí puedes hacer algo con el ID recibido (consultar base de datos, etc.)
    print(f"DEBUG> Botón presionado para la asignatura = {codigo_asignatura} : {nombre_asignatura}")
    return jsonify({'redirect_url': url_for('editarasignatura', codigo_asignatura=codigo_asignatura, nombre_asignatura=nombre_asignatura)})
    #return redirect(url_for('editarasignatura', codigo_asignatura=codigo_asignatura, nombre_asignatura=nombre_asignatura))

@app.route('/comandoeliminar', methods=['POST'])
def comandoeliminar():
    data = request.get_json()  # Recibe el ID del producto desde el frontend
    #item_id = data.get('id')
    codigo_asignatura = data.get('codigo_asignatura')
    nombre_asignatura = data.get('nombre_asignatura')
    # Aquí puedes hacer algo con el ID recibido (consultar base de datos, etc.)
    print(f"DEBUG> Botón presionado para la asignatura = {codigo_asignatura} : {nombre_asignatura}")
    return jsonify({'redirect_url': url_for('eliminarasignatura', codigo_asignatura=codigo_asignatura, nombre_asignatura=nombre_asignatura)})
    #return redirect(url_for('editarasignatura', codigo_asignatura=codigo_asignatura, nombre_asignatura=nombre_asignatura))

@app.route("/exportarmallapdf")
def exportarmallapdf():
    #Llamar comandos para generación de la malla
    os.system("wkhtmltoimage --format svg --user-style-sheet ./css/style_print.css tmp.html tmp.svg")
    os.system("svg2pdf tmp.svg malla_grafica.pdf")
 
    return jsonify({"respuesta":"PERO QUE ONDA"})


if __name__ == '__main__':
    # El parámetro debug=True recarga automáticamente la app si hay cambios en el código
    app.run(debug=True)
