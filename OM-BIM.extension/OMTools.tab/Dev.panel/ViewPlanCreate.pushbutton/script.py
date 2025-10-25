# -*- coding: utf-8 -*-
__title__     = "ViewFromLevels"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 1.1  
Date    = 22.10.2025  
_____________________________________________________________________
Description:
Create plan views automatically based on selected levels.
User can define:
- View type (Floor, Ceiling, Structural)
- Discipline (Architecture, MEP, etc.)
- Prefix and Suffix for naming
- Sub-specialty parameter (optional)
_____________________________________________________________________
How-to:
-> Run the script  
-> Select one or multiple Levels  
-> Choose View Type and Discipline  
-> Define Prefix/Suffix and SubSpecialty  
-> The script will create the views automatically  
_____________________________________________________________________
Last update:
- [21.12.2023] - 1.0 Initial release  
- [22.10.2025] - 1.1 Added Discipline, Prefix/Suffix and SubSpecialty options  
_____________________________________________________________________
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

def family_view_type(arg=None):
    data = dict()
    collector = (FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements())
    # Almacenamos:
    for famType in collector:
            name = Element.Name.GetValue(famType)
            data[name] = famType.Id
    #Check names
    claves = list(data.keys())
    if arg not in data:
        mensaje = "El tipo de vista '{}' no existe.\n\nTipos disponibles:\n{}\n\nIntentalo Nuevamente".format(
            arg, "\n".join(sorted(data.keys()))
        )
        forms.alert(mensaje, title="OMTools | View Generator", exitscript=True)
        return None

    # Retornar resultado
    return data[arg]

def vista_create(nivel, nombre=None, config = None):
    """
    Crea una vista de planta
    config puede contener: type, discipline, SubEspecialidad
    """
    if config is None:
        config = {}

    tipo = config.get("type", "Floor Plan")
    disciplina = config.get("discipline", "Fontaneria")
    SubEspecialidad = config.get("SubEspecialidad", None)

    if disciplina not in dic_disc.keys():
        mensaje = "El tipo de Disciplina '{}' no existe.\n\nTipos disponibles:\n{}\n\nIntentalo Nuevamente".format(
            disciplina, "\n".join(sorted(dic_disc.keys())))
        forms.alert(mensaje, title="OMTools | View Generator", exitscript=True)
        return None

    existing_views = [v for v in FilteredElementCollector(doc).OfClass(View).ToElements() if v.Name == nombre]
    if existing_views:
        print("La vista '{}' ya existe. Se omitió.".format(nombre))
        return None
    idTipo = family_view_type(tipo)

    with Transaction(doc, "Create New View") as t:
        t.Start()
        # Name
        vista = ViewPlan.Create(doc, idTipo, nivel.Id)
        vista.Name = nombre
        # View Discipline
        bic = BuiltInParameter.VIEW_DISCIPLINE
        vista.get_Parameter(bic).Set(int(dic_disc[disciplina]))

        # Asigna subespecialidad si aplica
        if SubEspecialidad:
            param = vista.LookupParameter("SubEspecialidad")
            param.Set(SubEspecialidad)
        t.Commit()
        return vista

## DICTS ###
#Entradas Config
dic_types = {"Planta Arquitectonica":"Floor Plan", "Planta Estructural":"Structural Plan", "Planta de Techo":"Ceiling Plan"}
dic_disc = {"Electricidad": ViewDiscipline.Electrical, "Estructuras":ViewDiscipline.Structural, "Coordinacion":ViewDiscipline.Coordination,
           "Arquitectura": ViewDiscipline.Architectural, "Mecanicas": ViewDiscipline.Mechanical, "Fontaneria":ViewDiscipline.Plumbing }



### COLLECTS ###
niveles = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
niv_dic = {x.Name:x for x in niveles}


### UI 1 ######
niveles_ui =forms.SelectFromList.show(sorted(niv_dic.keys()),title="OMTools | View Generator", multiselect=True, button_name = "Select item")
niveles_list = [niv_dic[x] for x in niveles_ui]

if not niveles_ui:
    mensaje = "No se selecciono niveles"
    forms.alert(mensaje, title="OMTools | View Generator", exitscript=True)


### UI 2 ######
components = [Label("Select Type of View"), ComboBox('ViewType', list(dic_types.keys())) ,
              Label("Select Discipline"), ComboBox('Discipline', list(dic_disc.keys())),
              Label("Prefix"), TextBox('Prefix', Text="") ,
              Label("Suffix"), TextBox('Suffix', Text=""),
              Label("SubEspecialidad (Parameter Optional)"), TextBox('SubEspecialidad', Text=""),Separator(),
              Button("Select")]


form = FlexForm("OMTools | View Generator", components)
form.show()
## RESULT ##
ViewType = dic_types[str(form.values["ViewType"])]
discipline = form.values["Discipline"]
Prefix = form.values["Prefix"]
Suffix = form.values["Suffix"]
SubEspecialidad = form.values["SubEspecialidad"]



views_created = 0
for lvl in niveles_list:
    nombre_vista = Prefix + lvl.Name + Suffix
    vista = vista_create(lvl, nombre_vista, config={"type":ViewType, "discipline":discipline, "SubEspecialidad":SubEspecialidad})
    if vista:
        views_created += 1

# Mostrar resultado final
Alert(
    "✅ Se crearon {} vistas estructurales correctamente.".format(views_created),
    title="OMTools | View Generator",
    header="Proceso completado",
    exit=False)

