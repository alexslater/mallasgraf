import pandas as pd
import os
import json
from flask import send_file
from datetime import date


class XLSConverter():

    def __init__(self):
        self.indice = {}
        self.datos = None


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

    def procesaExcel(self, filepath, filename):
        '''
        Docstring for procesaExcel
        
        :param self: Description
        :param filepath: Path al archivo que se desea convertir
        :param filename: Nombre del archivo XLSX que se leera

        Este método lee un archivo XLSX con datos de una malla curricular en formato de tabla
        y los devuelve organizado en una estructura de tipo JSON para almacenar en una base
        de datos SQL.
        
        '''
        #file_path = 'med.xlsx'
        data = pd.read_excel(filepath+filename)

        # Create a new dataframe to store the result
        data.drop_duplicates(inplace=True)

        #Renombrar las columnas
        data.rename(columns={"Area de Formacion":"Area", "Nombre Módulo": "Asignatura"}, inplace=True)
        data['Correlativo'] = data.groupby(['Area', 'Nivel']).cumcount() + 1
        data['Tipo'] = data['Area'].apply(self.determine_type)
        data['id'] = data.apply(lambda row: f"{row['Tipo']}-{row['Correlativo']}-{row['Nivel']}", axis=1)


        # Drop the 'Correlativo' column as it's no longer needed
        data = data.drop(columns=['Correlativo'])

        # Save the updated dataframe to a new Excel file
        #output_path = 'ejemplo_tabla_con_id.xlsx'
        #data.to_excel(output_path, index=False)
        #json_output = data.to_json(orient='records')
        
        max_nivel = int(data['Nivel'].max())
        print(f"XLS2JSON> Máximo nivel (numero total de semestres) = {max_nivel}")
        
        #Determinar el número máximo de asignaturas por grupo Nivel y area
        grouped_counts = data.groupby(['Nivel', 'Area']).size().reset_index(name='total_asignaturas')
        max_total_asignaturas_by_area = grouped_counts.groupby('Area')['total_asignaturas'].max().reset_index(name='max_total_asignaturas')


        json_data = data.to_dict(orient='records')
        #final_json_output = {
        #    "numero_semestres": max_nivel,
        #    "data": json_data
        #}

        final_json_output = {
        "numero_semestres": max_nivel,
        "total_asignaturas_por_nivel_y_area": grouped_counts.to_dict(orient='records'),
        "max_total_asignaturas_por_area": max_total_asignaturas_by_area.to_dict(orient='records'),
        "data": json_data
        }
        print(f"XLS2JSON> Máximo asignaturas por área: {max_total_asignaturas_by_area}")
        #json_output = json.dumps(final_json_output, indent=4)
        # Save the JSON output to a file
        # json_output_path = 'ejemplo_tabla_con_id.json'
        # with open(json_output_path, 'w') as file:
        #     file.write(json_output)
        #print(f"XLS2JSON> Output de salida de json:\n{final_json_output}")
        
        #Guarda los datos JSON en el objeto
        self.datos = final_json_output
        self.construirIndice()
        
        return final_json_output

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
            return self.datos['data'][self.indice[codigo_ubicacion]]['Asignatura']
        except:
            return ''
    
    def getSCT(self, codigo_ubicacion):
        try:
            return self.datos['data'][self.indice[codigo_ubicacion]]['SCT']
        except:
            return ''
    
    def getPrerequisito(self, codigo_ubicacion):
        try:
            return self.datos['data'][self.indice[codigo_ubicacion]]['Prerrequisitos']
        except:
            return ''
    
    def getN(self, codigo_ubicacion):
        try:
            return self.datos['data'][self.indice[codigo_ubicacion]]['ID Asignatura']
        except:
            return ''


    def getArea(self, codigo_ubicacion):
        try:
            return self.datos['data'][self.indice[codigo_ubicacion]]['Tipo']
        except:
            return ''

    def getNoAsignaturasporArea(self, area):
        print(f"DEBUG getNoAsignaturas> Solicita AREA = {area}")
        for mx in self.datos['max_total_asignaturas_por_area']:
            print(f"DEBUG getNoAsignaturas> {mx}")
            if mx['Area'] == area:
                print(f"DEBUG getNoAsignaturas> Retornando valor {mx['max_total_asignaturas']}")
                return mx['max_total_asignaturas']
        