# -*- coding: utf-8 -*-
__title__     = "ViewFromLevels"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 1.5  
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
- [21.10.2025] - 1.0 Initial release  
- [22.10.2025] - 1.1 Added Discipline, Prefix/Suffix and SubSpecialty options 
- [25.11.2025] - 1.5 Fixed Multi-Language support for View Type 

_____________________________________________________________________
Author: Oscar Mendoza"""  # Description

### EXTRA: You can delete this
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

def vista_create(nivel, nombre=None, config = None):
    """
    Creates a plan view.
    config may contain: type, discipline, SubSpecialty
    """
    ## CONFIG ##
    if config is None:
        config = {}
    tipo = config.get("type", "Floor Plan")
    disciplina = config.get("discipline", "Plumbing")
    SubEspecialidad = config.get("SubEspecialidad", None)

    ## code ##
    existing_views = [v for v in FilteredElementCollector(doc).OfClass(View).ToElements() if v.Name == nombre]
    if existing_views:
        print("The view '{}' already exists. Skipped.".format(nombre))
        return None
    idTipo = dic_ViewTypes[tipo]

    with Transaction(doc, "Create New View") as t:
        t.Start()
        # Name
        vista = ViewPlan.Create(doc, idTipo.Id, nivel.Id)
        vista.Name = nombre
        # View Discipline
        bic = BuiltInParameter.VIEW_DISCIPLINE
        vista.get_Parameter(bic).Set(int(dic_disc[disciplina]))

        # Assign SubSpecialty if applicable
        if SubEspecialidad:
            param = vista.LookupParameter("SubEspecialidad")
            if not param:
                mensaje2 = "The parameter does not exist"
                forms.alert(mensaje2, title="OMTools | View Generator", exitscript=True)
            if param:
                param.Set(SubEspecialidad)

        t.Commit()
        return vista


#Filter Views
View_Types = FilteredElementCollector(doc).OfClass(ViewFamilyType).ToElements()
View_Type_Plan = [vt for vt in View_Types if vt.ViewFamily == ViewFamily.FloorPlan][0]
View_Type_Ceiling = [vt for vt in View_Types if vt.ViewFamily == ViewFamily.CeilingPlan][0]
View_Type_StructuralPlan = [vt for vt in View_Types if vt.ViewFamily == ViewFamily.StructuralPlan][0]

## DICTS ###

dic_ViewTypes = {"Floor Plan": View_Type_Plan, "Ceiling Plan": View_Type_Ceiling, "Structural Plan": View_Type_StructuralPlan}

dic_disc = {"Electrical": ViewDiscipline.Electrical, "Structural":ViewDiscipline.Structural, "Coordination":ViewDiscipline.Coordination,
           "Architectural": ViewDiscipline.Architectural, "Mechanical": ViewDiscipline.Mechanical, "Plumbing":ViewDiscipline.Plumbing }


### COLLECTS ###
niveles = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Levels).WhereElementIsNotElementType().ToElements()
niv_dic = {x.Name:x for x in niveles}


### UI 1 ######
niveles_ui =forms.SelectFromList.show(sorted(niv_dic.keys()),title="OMTools | View Generator", multiselect=True, button_name = "Select item")

if not niveles_ui or niveles_ui is None:
    mensaje = "No levels were selected"
    forms.alert(mensaje, title="OMTools | View Generator", exitscript=True)

niveles_list = [niv_dic[x] for x in niveles_ui]

### UI 2 ######
components = [Label("Select Type of View"), ComboBox('ViewType', list(dic_ViewTypes.keys())) ,
              Label("Select Discipline"), ComboBox('Discipline', list(dic_disc.keys())),
              Label("Prefix"), TextBox('Prefix', Text="") ,
              Label("Suffix"), TextBox('Suffix', Text=""),
              Label("SubEspecialidad (Optional Parameter)"), TextBox('SubEspecialidad', Text=""),Separator(),
              Button("Select")]
form = FlexForm("OMTools | View Generator", components)
form.show()
if not form.values:
    mensaje = "No options were selected. Script cancelled."
    forms.alert(mensaje, title="OMTools | View Generator", exitscript=True)


## RESULT ##
ViewType = str(form.values["ViewType"])
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

# Final result
Alert(
    "✅ {} views were created successfully.".format(views_created),
    title="OMTools | View Generator",
    header="Process completed",
    exit=False)
