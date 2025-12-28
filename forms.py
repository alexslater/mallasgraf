from flask import Flask, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FileField, SelectField
from flask_wtf.file import FileRequired, FileAllowed    
from wtforms.validators import DataRequired

class XLSForm(FlaskForm):
    nombre_carrera = StringField("Nombre de la carrera: ", validators=[DataRequired()])
    archivo_xlsx = FileField("Archivo XLSX", validators=[DataRequired()])
    submit = SubmitField("Cargar")

class AsignaturaForm(FlaskForm):
    nombre_asignatura = StringField("Nombre Asignatura: ", validators=[DataRequired()])
    codigo_asignatura = StringField("Código Asignatura: ", validators=[DataRequired()])
    nivel_asignatura = StringField("Nivel: ", validators=[DataRequired()])
    #archivo_xlsx = FileField("Archivo XLSX", validators=[DataRequired()])
    submit = SubmitField("Ingresar")

class EditarForm(FlaskForm):
    nombre_asignatura = StringField("Nombre Asignatura: ", validators=[DataRequired()])
    codigo_asignatura = StringField("Código Asignatura: ", validators=[DataRequired()])
    nivel = StringField("Nivel: ", validators=[DataRequired()])
    area = StringField("Área: ", validators=[DataRequired()])
    sct = StringField("SCT: ", validators=[DataRequired()])
    codigo_ubicacion = StringField("Codigo ubcación: ", validators=[DataRequired()])
    #archivo_xlsx = FileField("Archivo XLSX", validators=[DataRequired()])
    submit = SubmitField("Guardar")

class AgregarForm(FlaskForm):
    nombre_asignatura = StringField("Nombre Asignatura: ", validators=[DataRequired()])
    codigo_asignatura = StringField("Código Asignatura: ", validators=[DataRequired()])
    nivel = StringField("Nivel: ", validators=[DataRequired()])
    area = SelectField("Área: ", choices=[('Básica', 'Básica'), ('Disciplinar', 'Disciplinar'), ('Electiva', 'Electiva')], validators=[DataRequired()])
    sct = StringField("SCT: ", validators=[DataRequired()])
    #archivo_xlsx = FileField("Archivo XLSX", validators=[DataRequired()])
    submit = SubmitField("Agregar")