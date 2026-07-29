# -*- coding: utf-8 -*-
__title__     = "ElemID"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 2.0
Date    = 27.06.2025
_____________________________________________________________________
Description:
Asign Element Id and Unique Id to Elements Model
_____________________________________________________________________
How-to:
-> Run the script
-> Choose Id or Unique Id Assingn
-> Select Project Parameters to asign
_____________________________________________________________________
Last update:
- [27.06.2025] - 1.0 RELEASE
- [15.02.2026] - 2.0 Fix Error Revit 26 No atribute Keys
________________________________________________________________________
Author: Oscar Mendoza"""  # Descripcion

### EXTRA: Tu puedes borrar esto
__helpurl__ = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
__min_revit_ver__ = 2021
__max_revit_ver__ = 2027

# ⬇️ IMPORTS
#--------------------------------------------------------------------------
import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms
import System
from rpw.ui.forms import *
#📦VARIABLES
#--------------------------------------------------------------------------
uidoc = __revit__.ActiveUIDocument   #type: Document
doc = __revit__.ActiveUIDocument.Document
selection = uidoc.Selection         #type: Selection

# 💻MAIN
#--------------------------------------------------------------------------
## FUNCTIONS ## #
builtInCategoriesName = ["OST_ShaftOpening", "OST_DuctAccessory", "OST_PipeAccessory", "OST_Coupler", "OST_VibrationManagement", "OST_DuctInsulations", "OST_PipeInsulations", "OST_DuctLinings", "OST_ElectricalFixtures", "OST_PlumbingFixtures", "OST_Parking", "OST_Areas", "OST_FabricAreas", "OST_Rebar", "OST_MEPAnalyticalFraming", "OST_StructuralFraming", "OST_CableTray", "OST_StairsRailing", "OST_MEPAnalyticalBus", "OST_Wire",
"OST_StructuralTendon", "OST_BridgeCables", "OST_MechanicalEquipment", "OST_Roads", "OST_StructuralFoundation", "OST_MEPAnalyticalWaterLoop", "OST_ElectricalCircuit", "OST_VerticalCirculation", "OST_DuctCurves", "OST_FlexDuctCurves", "OST_ElectricalLoadSet", "OST_MechanicalEquipmentSet", "OST_BridgeAbutments", "OST_Roofs", "OST_AudioVisualDevices", "OST_FireAlarmDevices", "OST_CommunicationDevices", "OST_MechanicalControlDevices", "OST_DataDevices",
"OST_LightingDevices", "OST_SecurityDevices", "OST_TelephoneDevices", "OST_Site", "OST_Entourage", "OST_PlumbingEquipment", "OST_FoodServiceEquipment", "OST_ZoneEquipment", "OST_Railing", "OST_CableConduit", "OST_ElectricalEquipment", "OST_SpecialityEquipment", "OST_MechanicalEquipment", "OST_Stairs", "OST_BridgeFraming", "OST_TemporaryStructure", "OST_RebarShape", "OST_ElectricalPowerSource",
"OST_MEPAnalyticalTransferSwitch", "OST_ExpansionJoints", "OST_LightingFixtures", "OST_FabricReinforcement", "OST_PlaceHolderDucts", "OST_PlaceHolderPipes", "OST_Mass", "OST_Furniture", "OST_GenericModel", "OST_Casework", "OST_Walls", "OST_Hardscape", "OST_Parts", "OST_StructuralColumns", "OST_BridgePiers", "OST_Bearings", "OST_FireProtection",
"OST_Doors", "OST_Ramps", "OST_FabricationDuctwork", "OST_AreaRain", "OST_PathRein", "OST_CurtainGrids", "OST_SwitchSystem", "OST_FabricationDuctworkStiffeners", "OST_StructuralStiffener", "OST_Sprinklers", "OST_Signage", "OST_MEPAnalyticalLoad", "OST_Curtains", "OST_FabricationHangers",
"OST_Floors", "OST_BridgeDecks", "OST_Ceilings", "OST_DuctTerminal", "OST_NurseCallDevices", "OST_CableTrayRun", "OST_ConduitRun", "OST_ElectricalAnalyticalTransformer", "OST_PipeCurves", "OST_FabricationPipework", "OST_FlexPipeCurves", "OST_Conduit", "OST_CableTrayFitting", "OST_DuctFitting", "OST_PipeFitting", "OST_ConduitFitting", "OST_Planting", "OST_Windows", "OST_StructuralTruss"]

###FUNCTIONS ###
def collect_elements (doc, list_bic):
    elements = []
    for name in list_bic:
        try:
            result = System.Enum.Parse(BuiltInCategory, name)
            list1 = list(FilteredElementCollector(doc).OfCategory(result).WhereElementIsNotElementType().ToElements())
            if len(list1) > 0:
                elements.extend(list1)
        except:
            pass
    return elements

def GetCategoryName(list_elements):
    uniqueCategories = {x.Category.Name: x.Category.Id for x in list_elements}
    return uniqueCategories.keys()

def GetCommonParameters(doc, elementos):
    if elementos is None or len(elementos) == 0:
        return []
    # Obtener parámetros del primer elemento
    parametersName = set( [p.Definition.Name for p in elementos[0].Parameters])
    # Recuperar nombres de parámetros comunes
    for element in elementos[1:]:
        elementParametersName = set([p.Definition.Name for p in element.Parameters])
        parametersName.intersection_update(elementParametersName)
    # Obtener parámetros finales
    parameters = [
        p for p in elementos[0].Parameters
        if p.Definition.Name in parametersName
        and p.StorageType == StorageType.String
        and not p.IsReadOnly]
    return parameters

## UI 1- CATEGORIES###
elements= collect_elements(doc, builtInCategoriesName)
categories = GetCategoryName(elements)

select_categories = forms.SelectFromList.show(categories, title = "Grid Locator - Select Categories",
                                              button_name = "Select", multiselect = True)
if not select_categories:
    forms.alert("Categories no choosen. Please try again",
                title = "OMBIM_AUTOMATION - Grid Locator",
                exitscript=True)

element_filters = [x for x in elements if x.Category.Name in select_categories]

## UI - 2.1 PARAMETERS ###

parametros = GetCommonParameters(doc, element_filters)
parametros_dic = {x.Definition.Name:x for x in parametros}

components = [Label("ID Param"), ComboBox("ID", parametros_dic),
              CheckBox("ID_Param", "Set ElementID?"),
              Label("UniqueId Param"), ComboBox("UniqueID", parametros_dic),
              CheckBox("UniqueID_Param", "Set UniqueID?"),
              Button("Select")]

form = FlexForm("OMBIM | Element Identifier", components)
form.show()
## CASE 1 : NOT SELECT ELEMENTS
if not form.values:
    forms.alert("No selection was made.\nPlease try again.", title = "OMBIM AUTOMATION", exitscript=True)

#COLLECT DECISIONS
ID_filter = form.values["ID_Param"]
param_ID = form.values["ID"]
UniqueID_filter = form.values["UniqueID_Param"]
param_uniqueID = form.values["UniqueID"]

## CASE 2 ID_FILTER

if ID_filter:
    with Transaction(doc, "Set OM_ID_BIM") as t:
        t.Start()
        for x in element_filters:
            param = x.LookupParameter(param_ID.Definition.Name)
            if param is not None:
                param.Set(str(x.Id))
        t.Commit()
    msg = ("Successfully assigned Element ID to elements.\n")
    msg += "Total elements processed: {}\n".format(len(element_filters))
    Alert(msg, title="OMBIM | Element Identifier", header="Element ID assignment complete", exit=False)
## CASE 3 UNIQUE_ID

if UniqueID_filter:
    with Transaction(doc, "Set OM_UNIQUEID_BIM") as t:
        t.Start()
        for x in element_filters:
            param = x.LookupParameter(param_uniqueID.Definition.Name)
            if param is not None:
                param.Set(str(x.UniqueId))
        t.Commit()
    msg = ("Successfully assigned Unique ID to elements.\n")
    msg += "Total elements processed: {}\n".format(len(element_filters))
    Alert(msg, title="OMBIM | Element Identifier", header="Unique ID assignment complete", exit=False)

