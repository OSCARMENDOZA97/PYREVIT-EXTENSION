# -*- coding: utf-8 -*-
__title__ ={
  "en_us": "OM Template",
  "en_gb":"OM Template",
  "es_es": "OM Plantilla"
}  # Nombre de del boton mostrado en Revit UI
__doc__ = """Version = 1.0
Fecha   = 25.02.2024
____________________________________________
Descripción
Esto es un archivo de plantilla para Pyrevit Scripts
____________________________________________
Como usarlo:
-> Click en el botón
-> Cambiar las configuraciones(optional)
-> Colocar los datos de entrada
___________________________________________
Ultimas actualizaciones:
- [25.06.2024] - 1.1 UPDATE - Nuevas caracteristicas
- [25.06.2024] - 1.0 ARCHIVO BASE
___________________________________________
Acciones:
- Revisar que la versión sea en 2021
__________________________________________
Author: Oscar Mendoza"""   # Descripcion

### EXTRA: Tu puedes borrar esto
__helpurl__ = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
__highlight__ = "new"
__min_revit_ver__ = 2021
__max_revit_ver__ = 2023
### EXTRAS
# ╦╔╦╗╔═╗╔═╗╦═╗╔╦╗╔═╗╔═╗╦╔═╗╔╗╔╔═╗╔═╗
# ║║║║╠═╝║ ║╠╦╝ ║ ╠═╣║  ║║ ║║║║║╣ ╚═╗
# ╩╩ ╩╩  ╚═╝╩╚═ ╩ ╩ ╩╚═╝╩╚═╝╝╚╝╚═╝╚═╝
#==================================================
import os, sys, datetime
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
from Autodesk.Revit.DB.Architecture import *

# pyRevit
from pyrevit import forms, revit, script

# .NET Importaciones
import clr
clr.AddReference('System')
from System.Collections.Generic import List
# List_ejemplo = List[ElementId]()

# ╦  ╦╔═╗╦═╗╦╔═╗╔╗ ╦  ╔═╗╔═╗
# ╚╗╔╝╠═╣╠╦╝║╠═╣╠╩╗║  ║╣ ╚═╗
#  ╚╝ ╩ ╩╩╚═╩╩ ╩╚═╝╩═╝╚═╝╚═╝
#==================================================

doc   = __revit__.ActiveUIDocument.Document  #Tipo: Document
uidoc = __revit__.ActiveUIDocument           #tipo: UIDocument
app   = __revit__.Application                # Application class

active_view  = doc.ActiveView
active_level = active_view.GenLevel
rvt_year     = int(app.VersionNumber)
PATH_SCRIPT  = os.path.dirname(__file__)

# VARIABLES GLOBALES

# ╔═╗╦═╗╦╔╗╔╔═╗╦╔═╗╔═╗╦
# ╠═╝╠╦╝║║║║║  ║╠═╝╠═╣║
# ╩  ╩╚═╩╝╚╝╚═╝╩╩  ╩ ╩╩═╝

# ⌨ INICIA EL CODIGO ACA

# 🔓 Use Transaction to Modify Document
# (Avoid placing inside of loops)
t = Transaction(doc, 'Change Name')

t.Start()                       #🔓 Start Transaction
# Changes Here...
t.Commit()                      #🔒 Commit Transaction

print('-'*50)
print('Script esta finalizado')
print('Plantilla fue elaborada por Oscar Mendoza.')