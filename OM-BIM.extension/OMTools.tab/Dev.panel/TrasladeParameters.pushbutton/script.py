# -*- coding: utf-8 -*-
__title__     = "MultiTransfer"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 2.0
Date    = 28.10.2026
_____________________________________________________________________
Description:
Transfer multiple parameters at once using SelectFromList and dynamic RPW FlexForm.
_____________________________________________________________________
How-to:
-> Run the script
-> Select Categories
-> Check multiple Source Parameters from the ListView
-> Map each Source Parameter to its Target Parameter in RPW FlexForm
_____________________________________________________________________
Last update:
- [28.10.2026] - 2.0 Multi-parameter RPW FlexForm version
________________________________________________________________________
Author: Oscar Mendoza"""

__helpurl__ = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
__min_revit_ver__ = 2021

# ⬇️ IMPORTS
#--------------------------------------------------------------------------
import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms
import System
from rpw.ui.forms import *

# 📦 VARIABLES
#--------------------------------------------------------------------------
uidoc = __revit__.ActiveUIDocument   #type: UIDocument
doc = __revit__.ActiveUIDocument.Document
selection = uidoc.Selection          #type: Selection

# 💻 MAIN
#--------------------------------------------------------------------------
builtInCategoriesName = [
    "OST_ShaftOpening", "OST_DuctAccessory", "OST_PipeAccessory", "OST_Coupler", "OST_VibrationManagement", 
    "OST_DuctInsulations", "OST_PipeInsulations", "OST_DuctLinings", "OST_ElectricalFixtures", "OST_PlumbingFixtures", 
    "OST_Parking", "OST_Areas", "OST_FabricAreas", "OST_Rebar", "OST_MEPAnalyticalFraming", "OST_StructuralFraming", 
    "OST_CableTray", "OST_StairsRailing", "OST_MEPAnalyticalBus", "OST_Wire", "OST_StructuralTendon", "OST_BridgeCables", 
    "OST_MechanicalEquipment", "OST_Roads", "OST_StructuralFoundation", "OST_MEPAnalyticalWaterLoop", "OST_ElectricalCircuit", 
    "OST_VerticalCirculation", "OST_DuctCurves", "OST_FlexDuctCurves", "OST_ElectricalLoadSet", "OST_MechanicalEquipmentSet", 
    "OST_BridgeAbutments", "OST_Roofs", "OST_AudioVisualDevices", "OST_FireAlarmDevices", "OST_CommunicationDevices", 
    "OST_MechanicalControlDevices", "OST_DataDevices", "OST_LightingDevices", "OST_SecurityDevices", "OST_TelephoneDevices", 
    "OST_Site", "OST_Entourage", "OST_PlumbingEquipment", "OST_FoodServiceEquipment", "OST_ZoneEquipment", "OST_Railing", 
    "OST_CableConduit", "OST_ElectricalEquipment", "OST_SpecialityEquipment", "OST_Stairs", "OST_BridgeFraming", 
    "OST_TemporaryStructure", "OST_RebarShape", "OST_ElectricalPowerSource", "OST_MEPAnalyticalTransferSwitch", 
    "OST_ExpansionJoints", "OST_LightingFixtures", "OST_FabricReinforcement", "OST_PlaceHolderDucts", "OST_PlaceHolderPipes", 
    "OST_Mass", "OST_Furniture", "OST_GenericModel", "OST_Casework", "OST_Walls", "OST_Hardscape", "OST_Parts", 
    "OST_StructuralColumns", "OST_BridgePiers", "OST_Bearings", "OST_FireProtection", "OST_Doors", "OST_Ramps", 
    "OST_FabricationDuctwork", "OST_AreaRain", "OST_PathRein", "OST_CurtainGrids", "OST_SwitchSystem", 
    "OST_FabricationDuctworkStiffeners", "OST_StructuralStiffener", "OST_Sprinklers", "OST_Signage", "OST_MEPAnalyticalLoad", 
    "OST_Curtains", "OST_FabricationHangers", "OST_Floors", "OST_BridgeDecks", "OST_Ceilings", "OST_DuctTerminal", 
    "OST_NurseCallDevices", "OST_CableTrayRun", "OST_ConduitRun", "OST_ElectricalAnalyticalTransformer", "OST_PipeCurves", 
    "OST_FabricationPipework", "OST_FlexPipeCurves", "OST_Conduit", "OST_CableTrayFitting", "OST_DuctFitting", 
    "OST_PipeFitting", "OST_ConduitFitting", "OST_Planting", "OST_Windows", "OST_StructuralTruss"
]

### FUNCTIONS ###
def collect_elements(doc, list_bic):
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
    uniqueCategories = {x.Category.Name: x.Category.Id for x in list_elements if x.Category is not None}
    return list(uniqueCategories.keys())

def GetCommonParameters(doc, elementos, only_writable=False):
    if elementos is None or len(elementos) == 0:
        return []
    # Obtener parámetros del primer elemento
    parametersName = set([p.Definition.Name for p in elementos[0].Parameters])
    # Recuperar nombres de parámetros comunes
    for element in elementos[1:]:
        elementParametersName = set([p.Definition.Name for p in element.Parameters])
        parametersName.intersection_update(elementParametersName)
    
    # Obtener parámetros finales (Todos para Origen, solo editables para Destino)
    if only_writable:
        parameters = [
            p for p in elementos[0].Parameters
            if p.Definition.Name in parametersName
            and not p.IsReadOnly
        ]
    else:
        parameters = [
            p for p in elementos[0].Parameters
            if p.Definition.Name in parametersName
        ]
    return parameters

def copy_parameter_value(source_param, target_param):
    """Copia el valor adaptando el tipo de almacenamiento entre Origen y Destino."""
    if not source_param or not target_param or target_param.IsReadOnly:
        return False
    if not source_param.HasValue:
        return False

    s_type = source_param.StorageType
    t_type = target_param.StorageType

    try:
        # Si el parámetro destino es Texto (String), convierte cualquier valor a String
        if t_type == StorageType.String:
            if s_type == StorageType.String:
                val = source_param.AsString()
            else:
                val = source_param.AsValueString()
                if not val:
                    if s_type == StorageType.Integer:
                        val = str(source_param.AsInteger())
                    elif s_type == StorageType.Double:
                        val = str(source_param.AsDouble())
                    elif s_type == StorageType.ElementId:
                        val = str(source_param.AsElementId())
            if val is not None:
                target_param.Set(val)
                return True

        # Si tienen el mismo StorageType
        elif s_type == t_type:
            if s_type == StorageType.Double:
                target_param.Set(source_param.AsDouble())
                return True
            elif s_type == StorageType.Integer:
                target_param.Set(source_param.AsInteger())
                return True
            elif s_type == StorageType.ElementId:
                target_param.Set(source_param.AsElementId())
                return True

        # Conversiones entre números y texto
        elif s_type == StorageType.Integer and t_type == StorageType.Double:
            target_param.Set(float(source_param.AsInteger()))
            return True
        elif s_type == StorageType.Double and t_type == StorageType.Integer:
            target_param.Set(int(round(source_param.AsDouble())))
            return True
        elif s_type == StorageType.String and t_type == StorageType.Double:
            target_param.Set(float(source_param.AsString()))
            return True
        elif s_type == StorageType.String and t_type == StorageType.Integer:
            target_param.Set(int(source_param.AsString()))
            return True
    except:
        return False
    return False


## UI 1 - CATEGORIES ###
elements = collect_elements(doc, builtInCategoriesName)
categories = GetCategoryName(elements)

select_categories = forms.SelectFromList.show(
    sorted(categories), 
    title="OMBIM - 1. Select Categories",
    button_name="Select Categories", 
    multiselect=True
)

if not select_categories:
    forms.alert(
        "Categories no choosen. Please try again",
        title="OMBIM_AUTOMATION - Parameter Transfer",
        exitscript=True
    )

element_filters = [x for x in elements if x.Category and x.Category.Name in select_categories]

## UI 2 - LISTVIEW DE PARÁMETROS DE ORIGEN ###
parametros_origen = GetCommonParameters(doc, element_filters, only_writable=False)
parametros_origen_nombres = sorted([x.Definition.Name for x in parametros_origen])

parametros_destino = GetCommonParameters(doc, element_filters, only_writable=True)
parametros_destino_dic = {x.Definition.Name: x for x in parametros_destino}

if not parametros_origen_nombres or not parametros_destino_dic:
    forms.alert(
        "No common editable parameters found for the selected categories.",
        title="OMBIM_AUTOMATION",
        exitscript=True
    )

# ListView para marcar todos los parámetros que quieres trasladar
selected_sources = forms.SelectFromList.show(
    parametros_origen_nombres,
    title="OMBIM - 2. Select Source Parameters to Transfer",
    button_name="Next: Map Target Parameters",
    multiselect=True
)

if not selected_sources:
    forms.alert(
        "No source parameters selected. Please try again.",
        title="OMBIM_AUTOMATION",
        exitscript=True
    )

## UI 3 - RPW FLEXFORM DINÁMICO (MAPEO ORIGEN -> DESTINO) ###
components = [
    Label("Asigna el parámetro de DESTINO para cada parámetro de ORIGEN:"),
    Separator()
]

# Construir dinámicamente los selectores en RPW según lo elegido en el ListView
for i, src_name in enumerate(selected_sources):
    components.append(Label("Origen [{}]  --->  Destino:".format(src_name)))
    components.append(ComboBox("target_{}".format(i), parametros_destino_dic))
    components.append(CheckBox("enable_{}".format(i), "Activar traslado de '{}'".format(src_name), default=True))
    components.append(Separator())

components.append(CheckBox("overwrite", "Sobrescribir valores existentes", default=True))
components.append(Button("Transfer Parameters"))

form = FlexForm("OMBIM | Multi-Parameter Transfer", components)
form.show()

if not form.values:
    forms.alert("No selection was made.\nPlease try again.", title="OMBIM AUTOMATION", exitscript=True)

## COLLECT DECISIONS ###
overwrite_flag = form.values["overwrite"]
transfer_pairs = [] # Lista de tuplas: (nombre_origen, nombre_destino)

for i, src_name in enumerate(selected_sources):
    is_enabled = form.values["enable_{}".format(i)]
    target_param_obj = form.values["target_{}".format(i)]
    
    if is_enabled and target_param_obj is not None:
        tgt_name = target_param_obj.Definition.Name
        if src_name != tgt_name:
            transfer_pairs.append((src_name, tgt_name))

if not transfer_pairs:
    forms.alert("No valid parameter pairs to transfer.", title="OMBIM AUTOMATION", exitscript=True)

## TRANSACTION - EJECUTAR TRASLADOS ###
results_counter = {pair: 0 for pair in transfer_pairs}

with Transaction(doc, "Set OM_MULTI_TRANSFER") as t:
    t.Start()
    for x in element_filters:
        for src_name, tgt_name in transfer_pairs:
            p_source = x.LookupParameter(src_name)
            p_target = x.LookupParameter(tgt_name)
            
            if p_source is not None and p_target is not None:
                if not overwrite_flag:
                    if p_target.StorageType == StorageType.String and p_target.AsString():
                        continue
                    elif p_target.StorageType != StorageType.String and p_target.HasValue:
                        continue
                
                if copy_parameter_value(p_source, p_target):
                    results_counter[(src_name, tgt_name)] += 1
    t.Commit()

## REPORTE FINAL CON RPW ALERT ###
msg = "Total elements in filter: {}\n".format(len(element_filters))
msg += "________________________________________\n"
for (src_name, tgt_name), count in results_counter.items():
    msg += "{} -> {}: {} elementos actualizados\n".format(src_name, tgt_name, count)

Alert(msg, title="OMBIM | Parameter Transfer", header="Multi-Parameter Transfer Complete", exit=False)