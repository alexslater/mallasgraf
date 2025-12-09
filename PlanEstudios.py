import pandas as pd
import os
import json
from flask import send_file
from datetime import date
from Asignatura import Asignatura


# Esta clase almacena datos de un plan de estudios JSON

class PlanEstudios():

    def __init__(self, datos_json):
        
        #Atributos de la clase
        self.indice = {}
        self.datos = datos_json
        self.numero_semestres = datos_json["numero_semestres"]
        self.total_asignaturas_por_nivel_y_area = datos_json["total_asignaturas_por_nivel_y_area"]
        self.max_total_asignaturas_por_area = datos_json["max_total_asignaturas_por_area"]
        self.asignaturas = {}

        #Llamar a construir indice.
        #self.construirIndice()
        self.crearAsignaturas(datos_json)

    def getPEJSON(self):
        """
        Docstring for getPEJSON
        
        :param self: Description
        
        Este método devuelve el plan de estudios en formato Diccionario (JSON) para hacer un payload
        y guardarlo en base de datos

        """
        d = {}
        d['numero_semestres'] = self.numero_semestres
        d['total_asignaturas_por_nivel_y_area'] = self.total_asignaturas_por_nivel_y_area
        d['max_total_asignaturas_por_area'] = self.max_total_asignaturas_por_area
        d['data'] = []

        for idx, it in self.asignaturas.items():
            a = {}
            a["ID Asignatura"] = it.getIdAsignatura()
            a["Nivel"] = it.getNivel()
            a["Asignatura"] = it.getAsignatura()
            a["SCT"] = it.getSCT()
            a["Prerrequisitos"] = it.getPrerrequisitos()
            a["Area"] = it.getNivel()
            a["Tipo"] = it.getTipo()
            a["id"] = it.getId()
            d['data'].append(a)

        return d

    def crearAsignaturas(self, datos_json):
        """
        Docstring for crearAsignaturas
        
        :param self: Description
        
        Este método crea las asignaturas cuando se invoca el constructor de la clase
        deja creado una diccionario objetos asignaturas
        """
        
        for d in datos_json["data"]:
            a = Asignatura()
            a.setIdAsignatura(d['ID Asignatura'])
            a.setNivel(d['Nivel'])
            a.setAsignatura(d['Asignatura'])
            a.setSCT(d['SCT'])
            a.setPrerrequisitos(d['Prerrequisitos'])
            a.setArea(d['Area'])
            a.setTipo(d['Tipo'])
            a.setId(d['id'])
            self.asignaturas[d['id']] = a
        #print(f"DEBUG crearAsignaturas>{self.asignaturas}")      

    """
        Este método determina el tipo de área a la que pertenece una asignatura.
        Recibe como parámetro un área y según el texto entrega una señal
    """
    def determine_type(self, area):
        if area == 'Básica':
            return 'ba'
        elif area == 'Disciplinar':
            return 'es'
        elif area == 'Electiva':
            return 'el'
        else:
            return 'un'

    """
        Este método toma lee un archivo excel y retorna un JSON con la información organizada para ser procesada
        por un script de JAVASCRIPT que dibuja una malla curricular
    """

    def construirIndice(self):
        datos_asignaturas = self.datos['data']
        i = 0
        for dt in datos_asignaturas:
            self.indice[dt['id']] = i
            i += 1
        print(f"DEBUG construirIndice> {self.indice}")
        return

    def getAsignatura(self, codigo_ubicacion):
        try:
            #print(f"DEBUG getAsignatura PLAN ESTUDIO> {self.asignaturas[codigo_ubicacion]}")
            #print(f"DEBUG getAsignatura PLAN ESTUDIO> {self.asignaturas[codigo_ubicacion].getAsignatura()}")
            
            return self.asignaturas[codigo_ubicacion].getAsignatura()
        except:
            return ''
        # try:
        #     return self.datos['data'][self.indice[codigo_ubicacion]]['Asignatura']
        # except:
        #     return ''
    
    def getSCT(self, codigo_ubicacion):
        try:
            print(f"DEBUG getSCT PLAN ESTUDIO> {self.asignaturas[codigo_ubicacion].getSCT()}")
            return self.asignaturas[codigo_ubicacion].getSCT()
        except:
            return ''
    
    def getPrerequisito(self, codigo_ubicacion):
        try:
            return self.asignaturas[codigo_ubicacion].getPrerrequisitos()
        except:
            return ''
    
    def getN(self, codigo_ubicacion):
        try:
            return self.asignaturas[codigo_ubicacion].getId()
        except:
            return ''

    def getArea(self, codigo_ubicacion):
        try:
            return self.asignaturas[codigo_ubicacion].getArea()
        except:
            return ''
    
    def getTipo(self, codigo_ubicacion):
        try:
            return self.asignaturas[codigo_ubicacion].getTipo()
        except:
            return ''

    def getNombreArea(self, codigo_ubicacion):
        try:
            print(f"DEBUG getNombreArea: {self.asignaturas[codigo_ubicacion].getNombreArea()}")
            return self.asignaturas[codigo_ubicacion].getNombreArea()
        except:
            return ''

    def getCodigoUbicacion(self, idasignatura):
        for idx, it in self.asignaturas.items():
            #print(it)
            #print(f"DEBUG getCodigoUbiacion> ASIG Id Asignatura = {it.getIdAsignatura()} | PARAM Id ASig = {idasignatura} ")
            if int(idasignatura) == it.getIdAsignatura():
                #print(f"DEBUG getCodigoUbicacion> {it.getIdAsignatura()} {it.getId()}")
                return it.getId()
        
    def updateAsignatura(self, codigo, asignatura, nivel, sct, area):
        """
        Docstring for updateAsignatura
        
        :param self: Description

        Este metodo realiza una actualización del objeto asignatura de la lista...

        """
        for idx, it in self.asignaturas.items():
            if int(codigo) == it.getIdAsignatura():
                self.asignaturas[it.getId()].setAsignatura(asignatura)
                self.asignaturas[it.getId()].setNivel(nivel)
                self.asignaturas[it.getId()].setSCT(sct)
                self.asignaturas[it.getId()].setArea(area)
                tipo = ""
                if area == "Básica":
                    tipo = "ba"
                elif area == "Disciplinar":
                    tipo = "es"
                elif area == "Electiva":
                    tipo = "el"
                idasignatura = f"{tipo}-{codigo}-{nivel}"
                self.asignaturas[it.getId()].setTipo(tipo)
                self.asignaturas[it.getId()].setId(idasignatura)
                



    def getNoAsignaturasporArea(self, area):
        print(f"DEBUG getNoAsignaturas> Solicita AREA = {area}")
        for mx in self.datos['max_total_asignaturas_por_area']:
            print(f"DEBUG getNoAsignaturas> {mx}")
            if mx['Area'] == area:
                print(f"DEBUG getNoAsignaturas> Retornando valor {mx['max_total_asignaturas']}")
                return mx['max_total_asignaturas']
        