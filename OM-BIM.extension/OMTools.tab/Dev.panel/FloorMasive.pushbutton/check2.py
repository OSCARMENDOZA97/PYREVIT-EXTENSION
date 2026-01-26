# -*- coding: utf-8 -*-
__title__     = "Floor Massive"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 1.0
Date    = 24.01.26
_____________________________________________________________________
Description:
Select Linked Elements based on selected in UI:
- Revit Linked Project
- Element Categories 
_____________________________________________________________________
How-to:
-> Run the script
-> Select Linked Revit Project
-> Select Revit Categories
-> Pick Linked Elements matching selected criteria
_____________________________________________________________________
Last update:
- [21.12.2023] - 1.0 RELEASE
- [21.02.2025] - 1.1 BuiltinCategory Invalid
________________________________________________________________________
Author: Oscar Mendoza"""  # Descripcion

### EXTRA: Tu puedes borrar esto
__helpurl__ = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
__min_revit_ver__ = 2021
__max_revit_ver__ = 2026

# ⬇️ IMPORTS
#--------------------------------------------------------------------------
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms

#📦VARIABLES
#--------------------------------------------------------------------------
uidoc = __revit__.ActiveUIDocument   #type: Document
doc = __revit__.ActiveUIDocument.Document
selection = uidoc.Selection         #type: Selection

# 💻MAIN
#--------------------------------------------------------------------------
# 1. Obtener todos los Rooms válidos (colocados y con área > 0)
Rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()

n = 0
for x in Rooms:
    n += 1
    room_name = x.get_Parameter(
        BuiltInParameter.ROOM_NAME
    ).AsString()
    if "casilleros" in room_name or "asientos" in room_name:
        print("El nombre del room es {} : {}".format(Element.Name.GetValue(x),
                                                     doc.GetElement(x.LevelId).Name))

print("\n\nLa cantidad de rooms es {}".format(n))



# 2. Leer el parámetro de acabado de suelo del Room
# 3. Crear un diccionario {CodigoSuelo : [Rooms]}
# 4. Obtener todos los tipos de suelos y realizar lista (-) (0)
# 4. Obtener el valor del room de los tipos de suelos
# 7. Obtener las curvas límite de cada Room válido
# 8. Agrupar Rooms por código de suelo y nivel
# 9. Crear los suelos usando el Floor Type, curvas y nivel correspondientes