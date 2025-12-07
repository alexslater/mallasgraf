class Asignatura():

    def __init__(self):
        self.__id_asignatura = 0
        self.__nivel = 0
        self.__asignatura = ""
        self.__SCT = 0
        self.__prerrequisitos = []
        self.__area = ""
        self.__tipo = ""
        self.__id = ""
        
    def setIdAsignatura(self, id):
        self.__id_asignatura = id

    def getIdAsignatura(self):
        return self.__id_asignatura
    
    def setNivel(self, nivel):
        self.__nivel = nivel

    def getNivel(self):
        return self.__nivel
    
    def setAsignatura(self, asignatura):
        self.__asignatura = asignatura

    def getAsignatura(self):
        return self.__asignatura
    
    def setSCT(self, sct):
        self.__SCT = sct

    def getSCT(self):
        return self.__SCT
    
    def setPrerrequisitos(self, prerrequisitos):
        self.__prerrequisitos = prerrequisitos

    def getPrerrequisitos(self):
        return self.__prerrequisitos
    
    def setArea(self, area):
        self.__area = area
    
    def getArea(self):
        if self.__area == "Básica":
            return "ba"
        elif self.__area == "Disciplinar":
            return "es"
        elif self.__area == "Electiva":
            return "el"
        else:
            return "un"
    
    def setTipo(self, tipo):
        self.__tipo = tipo

    def getTipo(self):
        return self.__tipo
    
    def setId(self, id):
        self.__id = id

    def getId(self):
        return self.__id
    