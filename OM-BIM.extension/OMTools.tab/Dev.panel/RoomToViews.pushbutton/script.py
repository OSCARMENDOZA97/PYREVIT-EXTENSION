# -*- coding: utf-8 -*-
__title__     = "RoomsToViews"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 1.1
Date    = 28.11.2025
_____________________________________________________________________
Description:
Create plan views automatically based on selected Rooms.  
The user can define:
- Level to filter rooms
- One or multiple Rooms
- View Type (Floor Plan / Ceiling Plan)
- Discipline (Architecture, Electrical, etc.)
- Custom Prefix and Suffix for naming
- View Template to apply

The script:
→ Filters the rooms by the selected Level  
→ Creates views for each room with automatic naming  
→ Applies crop region based on Room BoundingBox  
→ Applies selected View Template  
_____________________________________________________________________
How-to:
1. Run the script  
2. Select Level  
3. Select Rooms from the list  
4. Select View Type, Discipline, Prefix, Suffix and Template  
5. The script creates the views and applies crop & template automatically  
_____________________________________________________________________
Last update:
- [21.12.2023] - 1.0 Initial Release
- [28.11.2025] - 1.1 Room-based Views + crop + template application
_____________________________________________________________________
Author: Oscar Mendoza"""

### EXTRA: Tú puedes borrar esto
__helpUrl__ = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
__min_revit_ver__ = 2021
__max_revit_ver__ = 2026



# ⬇️ IMPORTS
#--------------------------------------------------------------------------
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
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
#Filter Rooms by Level
levels = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
levels_dic = {x.Name:x for x in levels}

def check_level(level, element):
    """Check Element is level correct"""
    if element.Level.Id == level.Id:
        return True

all_rooms = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Rooms).WhereElementIsNotElementType().ToElements()


def vista_create(nivel, nombre=None, tipo= None, config = None):
    """
    Creates a plan view.
    config may contain: type, discipline, SubSpecialty
    """
    ## CONFIG ##
    if config is None:
        config = {}
    disciplina = config.get("discipline", "Coordination")

    ## code ##
    existing_views = [v for v in FilteredElementCollector(doc).OfClass(View).ToElements() if v.Name == nombre]
    if existing_views:
        print("The view '{}' already exists. Skipped.".format(nombre))
        return None
    idTipo = dic_ViewTypes[tipo]

    with Transaction(doc, "Create New View") as t:
        t.Start()
        # Name
        view = ViewPlan.Create(doc, idTipo.Id, nivel.Id)
        view.Name = nombre
        # View Discipline
        bic = BuiltInParameter.VIEW_DISCIPLINE
        view.get_Parameter(bic).Set(int(dic_disc[disciplina]))

        t.Commit()
        return view

#bbox.Min = Esquina inferior / Esquina superior bbox Max
def offset_bbox(bbox, offset):
    min_x = bbox.Min.X - offset
    min_y = bbox.Min.Y - offset
    min_z = bbox.Min.Z - offset

    max_x = bbox.Max.X + offset
    max_y = bbox.Max.Y + offset
    max_z = bbox.Max.Z + offset

    # Crear nuevo bounding box
    new_bbox = BoundingBoxXYZ()
    new_bbox.Min = XYZ(min_x, min_y, min_z)
    new_bbox.Max = XYZ(max_x, max_y, max_z)

    return new_bbox
floorPlans = []
def view_plan_room(view, offset):
    """Crea una vista por habitación con una escala de vista 1:50"""
    bbox = room.BoundingBox[doc.ActiveView]
    new_bbox = offset_bbox(bbox,offset)
    with Transaction(doc, "ViewPlanRoom") as t:
        t.Start()
        view.CropBox = new_bbox
        view.CropBoxActive = True
        view.CropBoxVisible = True
        view.Scale = 50
        floorPlans.append(view)
        t.Commit()
        return floorPlans

def unique_name(name_general):
    """Genera un nombre único si la vista ya existe."""
    existing_names = {v.Name for v in FilteredElementCollector(doc).OfClass(View).ToElements()}
    nombre = name_general
    contador = 2

    while nombre in existing_names:
        nombre = "{} ({})".format(name_general, contador)
        contador += 1

    return nombre

def toList(input):
    #Return iterable if available, a list of 1 otherwise
    if hasattr(input, "__iter__") and not isinstance(input, basestring):
        return input
    else:
        return [input]

templateList = []
templateNameList=[]


def apply_template_by_name(view, template_name):
    """Aplica una plantilla a una vista según el nombre."""

    # Buscar plantilla
    template = next(
        (v for v in FilteredElementCollector(doc).OfClass(View).ToElements()
         if v.IsTemplate and v.Name == template_name),
        None
    )

    if not template:
        forms.alert("La plantilla '{}' no existe.".format(template_name), exitscript=True)
        return False

    # Aplicar la plantilla
    with Transaction(doc, "Apply View Template") as t:
        t.Start()
        view.ViewTemplateId = template.Id
        t.Commit()

    return True

### UI ###
#Filter Views to UI ###
View_Types = FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
View_Type_Plan = [vt for vt in View_Types if vt.ViewFamily == ViewFamily.FloorPlan][0]
View_Type_Ceiling = [vt for vt in View_Types if vt.ViewFamily == ViewFamily.CeilingPlan][0]

## DICTS UI  ###
dic_ViewTypes = {"Floor Plan": View_Type_Plan, "Ceiling Plan": View_Type_Ceiling}
dic_disc = {"Electrical": ViewDiscipline.Electrical, "Structural":ViewDiscipline.Structural, "Coordination":ViewDiscipline.Coordination,
           "Architectural": ViewDiscipline.Architectural, "Mechanical": ViewDiscipline.Mechanical, "Plumbing":ViewDiscipline.Plumbing }

### UI 1 ##
# 1️⃣Select Level
level_select = SelectFromList('Test Window', levels_dic)

### UI 2 ##
#2️⃣ Filter rooms by level
filtered_rooms_level = [room for room in all_rooms if check_level(level_select, room)]
room_dictionary = {x.get_Parameter(BuiltInParameter.ROOM_NAME).AsString():x for x in filtered_rooms_level}
room_ui =forms.SelectFromList.show(sorted(room_dictionary.keys()),title="OMTools | Room To Views", multiselect=True, button_name = "Select item")


if not room_ui or room_ui is None:
    mensaje = "No Rooms were selected"
    forms.alert(mensaje, title="OMTools | Room to views", exitscript=True)

room_select = [room_dictionary[x] for x in room_ui]

#Iterable element
if isinstance(room_select, list):
    rooms = room_select
else:
    rooms =[room_select]

### UI 3 ###
components = [Label("Select Type of View"), ComboBox('ViewType', list(dic_ViewTypes.keys())),
              Label("Select Discipline"), ComboBox('Discipline', list(dic_disc.keys())),
              Label("Prefix"), TextBox('Prefix', Text=""),
              Label("Suffix"), TextBox('Suffix', Text=""),
              Label("TempName"), TextBox('TempName', Text=""),
              Button("Select")]

form = FlexForm("OMTools | Rooms To Views", components)
form.show()
if not form.values:
    mensaje = "No options were selected. Script cancelled."
    forms.alert(mensaje, title="OMTools | View Generator", exitscript=True)

## RESULT ####
ViewType = str(form.values["ViewType"])
discipline = form.values["Discipline"]
Prefix = form.values["Prefix"]
Suffix = form.values["Suffix"]
TempName = form.values["TempName"]

## CODE ##

views_created = 0
for room in rooms:
    nombre_general = Prefix + room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString() + Suffix
    nombre_vista = unique_name(nombre_general)
    #1️⃣Create View
    vista = vista_create(level_select, nombre_vista, ViewType, config={"discipline":discipline})
    #2️⃣Crop View
    view_plan_room(vista,2)
    #3️⃣Template
    template_name = TempName
    apply_template_by_name(vista, template_name)
    if vista:
        views_created += 1


# Final result
Alert(
    "✅ {} views were created successfully.".format(views_created),
    title="OMTools | View Generator",
    header="Process completed",
    exit=False)

"""
for x in filtered_rooms_level:
    print("Id {}, Nombre {}".format(x.Id, Element.Name.GetValue(x)))
print("Cantidad de elementos {}".format(len(filtered_rooms_level)))
"""