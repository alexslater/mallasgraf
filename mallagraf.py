from flask import Flask, render_template, request, redirect, url_for, jsonify, flash, send_from_directory
from forms import XLSForm, EditarForm
from werkzeug.utils import secure_filename
import os
from xls2json import XLSConverter
import uuid
import sqlite3
import json


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
                   jsonpayload text)''')
    conn.commit()

    
    #Insertar registro
    datos_malla['carrera'] = nombre_carrera
    cursor.execute(f"""INSERT INTO mallas VALUES ('{filename}', '{nombre_carrera}', '{json.dumps(datos_malla)}') """)
    conn.commit()

    #result=cursor.execute("SELECT * FROM mallas")
    #return redirect(url_for('renderizamalla', idmalla=filename))
    return render_template("tablamallas.html", listaasignaturas=datos_malla['data'], filename=filename, nombre_carrera=nombre_carrera)


@app.route("/renderizamalla/<filename>/<nombre_carrera>")
def renderizamalla(filename, nombre_carrera):
    xlsconverter = XLSConverter()
    datos_malla = xlsconverter.procesaExcel("./uploads/", filename)
    print(f"DEBUG renderizamalla> Nombre de archivo pasado {filename}")
    print(f"DEBUG renderizamalla> Nombre de carrera pasado {nombre_carrera}")
    print(f"DEBUG renderizamalla> {datos_malla}")
    numero_semestres = datos_malla['numero_semestres']
    max_asig_por_area = datos_malla["max_total_asignaturas_por_area"]
   
    
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
    
    areas = ['Específica', 'Básica', 'Electiva']
    area_classes = ['area-es', 'area-ba', 'area-el']
    
    #Acá se preparan los cuadros de áreas específica, básica y electiva
    #esto se ocupaba en javascript para calcular el tamaño del cuadro
    #const px_ba = ((max_asig_basica+1)*120) - ((max_asig_basica+1)*20)

    for idx, area in enumerate(areas):
        max_asig = max_asig_por_area[idx]["max_total_asignaturas"]
        max_asig_area = xlsconverter.getNoAsignaturasporArea(area)
        px_ba = ((max_asig_area+1)*115) - ((max_asig_area+1)*15)
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
                    <div class="data-celda fs-6 text-white area-{xlsconverter.getArea(idasig)}">
                    {xlsconverter.getAsignatura(idasig)}
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
    os.system(f"wkhtmltoimage --format svg --user-style-sheet ./static/css/style_print.css ./html_render/{filename}.html ./svg/{filename}.svg")
    os.system(f"svg2pdf ./svg/{filename}.svg ./pdf/{filename}.pdf")
    return render_template("rendermalla.html", html=html, filename=filename)

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

@app.route("/listarasignaturas")
def listarasignaturas():
    return render_template("listarasignaturas.html", asignaturas=datos_asignaturas)

@app.route("/editarasignatura/<codigo_asignatura>/<nombre_asignatura>")
def editarasignatura(codigo_asignatura, nombre_asignatura):
    editar_form = EditarForm()
    return render_template("editarasignatura.html", template_form=editar_form, codigo_asignatura=codigo_asignatura, nombre_asignatura=nombre_asignatura)

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
