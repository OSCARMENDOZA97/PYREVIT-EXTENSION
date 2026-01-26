# -*- coding: utf-8 -*-
__title__     = "Floor Massive"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 1.0
Date    = 24.01.26
_____________________________________________________________________
Description:
Create Floors automatically based on Room floor finish information.
The script:
- Collects valid Rooms (placed and with area > 0)
- Groups Rooms by Floor Finish parameter
- Matches Room floor codes with existing Floor Types (Type Mark)
- Creates Floors using Room boundaries, Floor Type and Level
_____________________________________________________________________
How-to:
-> Run the script
-> Script reads Room Floor Finish values
-> Matching Floor Types must exist (Type Mark)
-> Floors are created automatically per Room
________________________________________________________________________
Author: Oscar Mendoza"""  # Descripción

### EXTRA: Tú puedes borrar esto
__help_url__ = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
__min_revit_ver__ = 2021
__max_revit_ver__ = 2026

# ⬇️ IMPORTS
#--------------------------------------------------------------------------
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms
from System.Collections.Generic import List
from pyrevit import forms
import clr, sys
clr.AddReference("System")
from rpw.ui.forms import *

#📦VARIABLES
#--------------------------------------------------------------------------
uidoc = __revit__.ActiveUIDocument   #type: Document
doc = __revit__.ActiveUIDocument.Document
selection = uidoc.Selection         #type: Selection

# 💻MAIN
#--------------------------------------------------------------------------
# 1. Obtener todos los Rooms válidos (colocados y con área > 0)
def check_room(room1):
    """Check if room is placed and area is more than 0"""
    room_area = room1.Area
    if room_area > 0 and room1.Location:
        return True

def get_values_from_keys(key_list, data_dict):
    return [data_dict[k] for k in key_list if k in data_dict]

def list_flatten(lista):
    """Flatten the list
    Input : list
    Output: Flattened list"""
    output = []
    if isinstance(lista,list):
        for sub in lista:
            if isinstance(sub,list):
                output.extend(list_flatten(sub))
            else:
                output.append(sub)
    else:
        output = "Check. Insert List"
    return output

def repeat_by_length (list_a,list_b):
    """
    Input:
    - list_a : list of lists
    - list_b : list
    Output:
    - list with repeated values based on sublist length
    """
    result = []
    for x,y in zip(list_a, list_b):
        number = len(x)
        result.extend([y]*number)
    return result

def room_loops(room2):
    """
    Input:
        room: <Autodesk.Revit.DB.Architecture.Room>
    Output
        curveLoop
    """
    boundaries = room2.GetBoundarySegments(SpatialElementBoundaryOptions()) # Return list
    loops = List[CurveLoop]()

    for boundary in boundaries:
        cl = CurveLoop()
        for seg in boundary:
            cl.Append(seg.GetCurve())
        loops.Add(cl)

    return loops

def get_room_by_floor_code(doc):
    """input: none
    output: dict(floor_name,room)"""
    Rooms = (FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).
             WhereElementIsNotElementType().ToElements())
    filtered_rooms = [room for room in Rooms if check_room(room)]
    floor_dic= {}
    for room in filtered_rooms:
        floor_code = room.get_Parameter(BuiltInParameter.ROOM_FINISH_FLOOR).AsValueString()
        # Crea lista si no existe
        if floor_code not in floor_dic:
            floor_dic [floor_code] = []
        # Agregar room
        floor_dic[floor_code].append(room)
    return floor_dic

def get_floor_types_by_mark(doc):
    suelos_typ = (FilteredElementCollector(doc)
                  .OfCategory(BuiltInCategory.OST_Floors)
                  .WhereElementIsElementType()
                  .ToElements())
    suelos_typ_name = [elem.get_Parameter(BuiltInParameter.ALL_MODEL_TYPE_MARK).AsValueString()
        for elem in suelos_typ]
    dic_suelos_type = dict(zip(suelos_typ_name, suelos_typ))
    return dic_suelos_type

# 2. Crear un diccionario {CodigoSuelo: [Rooms]}
dic_fName_Room = get_room_by_floor_code(doc)
# 3. Obtener todos los tipos de suelos
dic_floor = get_floor_types_by_mark(doc)
#4. Comprobar que los suelos existan en la lista de los codigos
List_floorFilter = [x for x in dic_floor.keys() if x in dic_fName_Room.keys() and not x == None]
#6. Lista de diccionarios con base en lista filtrada
List_room = get_values_from_keys(List_floorFilter, dic_fName_Room)
List_floor = get_values_from_keys(List_floorFilter, dic_floor)

#7. Lista aplanadas
list_room = list_flatten(List_room)
list_floor = repeat_by_length(List_room,List_floor)

# 9. Crear los suelos usando el Floor Type, curvas y nivel correspondientes

with Transaction(doc, "FloorMassive") as t:
    t.Start()

    for room, floor in zip(list_room, list_floor):
        try:
            Floor.Create(doc, room_loops(room), floor.Id, room.LevelId)
        except Exception as e:
            print("ERROR en room:", room.Id)
            print(e)

    t.Commit()

# Final result
Alert(
    "✅ {} floors were created successfully.".format(len(list_room)),
    title="OMTools | Floor Massive",
    header="Process completed",
    exit=False)





# 7. Obtener las curvas límite de cada Room válido
# 8. Agrupar Rooms por código de suelo y nivel
