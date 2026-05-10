# -*- coding: utf-8 -*-
__title__     = "Grid Locator"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 1.0
Date    = 10.05.2026
_____________________________________________________________________
Description:

Automatically detects the nearest grids of selected Revit elements
and writes the grid references into a selected parameter.

Features:
- Supports point, curve and surface elements
- Horizontal and vertical grid detection
- Optional distance calculation
- Custom suffix insertion
- Multiple category support

_____________________________________________________________________
How-to:

-> Run the script
-> Select categories
-> Select parameter
-> Optional: include distances / suffix
-> Press Select

_____________________________________________________________________
Last update:

- [10.05.2026] - 1.0 RELEASE
________________________________________________________________________
Author: Oscar Mendoza
"""  # Descripcion

### EXTRA: Tu puedes borrar esto
__helpurl__ = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
__min_revit_ver__ = 2021
__max_revit_ver__ = 2026

# ⬇️ IMPORTS
#--------------------------------------------------------------------------
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
import System
from pyrevit import forms
from rpw.ui.forms import *
import math

#📦VARIABLES
#--------------------------------------------------------------------------
uidoc = __revit__.ActiveUIDocument   #type: Document
doc = __revit__.ActiveUIDocument.Document
selection = uidoc.Selection         #type: Selection

# 💻MAIN
#--------------------------------------------------------------------------
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

def GetLocation(elements):

    locations = []
    for element in elements:
        try:
            # ELEMENTOS CON CURVA - VIGA
            if isinstance(element.Location, LocationCurve):
                curve = element.Location.Curve
                startPoint = curve.GetEndPoint(0)
                endPoint = curve.GetEndPoint(1)
                locations.append([XYZ(startPoint.X, startPoint.Y, 0),
                    XYZ(endPoint.X, endPoint.Y, 0)])

            # ELEMENTOS CON PUNTO - COLUMNA
            elif isinstance(element.Location, LocationPoint):
                # COLUMNAS
                if element.Category.BuiltInCategory == BuiltInCategory.OST_StructuralColumns:
                    bbox = element.get_BoundingBox(None)
                    minP = bbox.Min
                    maxP = bbox.Max

                    a = abs(minP.X - maxP.X)
                    b = abs(minP.Y - maxP.Y)
                    distancia = max(a, b)
                    limit = 0.50

                    if distancia > limit:
                        if distancia == a:
                            startPoint = XYZ(minP.X, (minP.Y + maxP.Y) / 2, 0)
                            endPoint = XYZ(maxP.X, (minP.Y + maxP.Y) / 2, 0)
                        else:
                            startPoint = XYZ((minP.X + maxP.X) / 2, minP.Y, 0)
                            endPoint = XYZ((minP.X + maxP.X) / 2, maxP.Y, 0)
                        locations.append([startPoint, endPoint])

                    else:
                        point = element.Location.Point
                        locations.append([XYZ(point.X, point.Y, 0)])

                # OTROS ELEMENTOS CON PUNTO
                else:

                    point = element.Location.Point
                    locations.append([XYZ(point.X, point.Y, 0)])

            # ELEMENTOS SIN LOCATION - PISOS
            else:
                try:
                    solid = GetSolidElement(element)
                    vertices = GetVerticesOfSolid(solid)
                    maxX = sorted(vertices, key=lambda v: v.X, reverse=True)[0]
                    minX = sorted(vertices, key=lambda v: v.X)[0]
                    maxY = sorted(vertices, key=lambda v: v.Y, reverse=True)[0]
                    minY = sorted(vertices, key=lambda v: v.Y)[0]
                    locations.append([minX,maxX,minY,maxY])

                except:
                    bbox = element.get_BoundingBox(doc.ActiveView)
                    minPoint = bbox.Min
                    maxPoint = bbox.Max

                    locations.append([
                        XYZ(minPoint.X, minPoint.Y, 0),
                        XYZ(maxPoint.X, minPoint.Y, 0),
                        XYZ(minPoint.X, minPoint.Y, 0),
                        XYZ(minPoint.X, maxPoint.Y, 0)])
        except Exception as e:

            try:
                catName = element.Category.Name
            except:
                catName = "SIN CATEGORIA"

            print("ERROR EN CATEGORIA: {}".format(catName))
            print("ELEMENT ID: {}".format(element.Id))
            print("ERROR: {}".format(e))
    return locations
def grid_vertical_horizontal(grids):
    horizontal = []
    vertical = []

    for grid in grids:
        vec = grid.Curve.ComputeDerivatives(0.5, True).BasisX.Normalize()
        angle = math.degrees(vec.AngleTo(XYZ.BasisX))

        if angle <= 45 or angle >= 315 or 135 <= angle <= 225:
            horizontal.append(grid)
        else:
            vertical.append(grid)

    return horizontal, vertical

def get_names_and_distances(locations, grids_horizontal, grids_vertical, include_distance=True):

    names_and_distances = []

    for location in locations:

        name_horizontal = ""
        name_vertical = ""

        ## COLUMNAS##
        if len(location) == 1:

            point = location[0]

            closest_h = closest_grid(grids_horizontal, point)
            closest_v = closest_grid(grids_vertical, point)

            distance_h = round(closest_h.Distance * 0.3048, 2)
            distance_v = round(closest_v.Distance * 0.3048, 2)

            name_horizontal = "{}({}m)".format(closest_h.NameGrid, distance_h) if include_distance else closest_h.NameGrid
            name_vertical = "{}({}m)".format(closest_v.NameGrid, distance_v) if include_distance else closest_v.NameGrid

        ## BEAMS ###
        elif len(location) == 2:

            horizontal_values = []
            vertical_values = []

            for point in location:

                closest_h = closest_grid(grids_horizontal, point)
                closest_v = closest_grid(grids_vertical, point)

                distance_h = round(closest_h.Distance * 0.3048, 2)
                distance_v = round(closest_v.Distance * 0.3048, 2)

                horizontal_values.append("{}({}m)".format(closest_h.NameGrid, distance_h) if include_distance else closest_h.NameGrid)
                vertical_values.append("{}({}m)".format(closest_v.NameGrid, distance_v) if include_distance else closest_v.NameGrid)

            name_horizontal = "/".join(horizontal_values)
            name_vertical = "/".join(vertical_values)


        ## FLOOR ###
        elif len(location) >= 4:

            horizontal_values = []
            vertical_values = []

            for i in range(2):

                closest_h = closest_grid(grids_horizontal, location[i + 2])
                closest_v = closest_grid(grids_vertical, location[i])

                horizontal_values.append(closest_h.NameGrid)
                vertical_values.append(closest_v.NameGrid)

            name_horizontal = "/".join(horizontal_values)
            name_vertical = "/".join(vertical_values)

        names_and_distances.append([name_horizontal, name_vertical])

    return names_and_distances
def closest_grid(grids, point):
    """
    Obtiene el grid más cercano a un punto XYZ.
    """

    min_distance = float("inf")
    closest = None

    for grid in grids:
        curve = grid.Curve
        projected = curve.Project(point)
        if projected:
            distance = projected.Distance
            if distance < min_distance:
                min_distance = distance
                closest = {
                    "Grid": grid,
                    "NameGrid": grid.Name,
                    "Distance": distance}

    return type("ClosestGrid", (object,), closest)
def message_final(elements):
    msg = ""
    msg += "\n  Total elements processed : {}\n".format(len(elements))

    Alert(msg, title="OMBIM-AUTOMATION", header="Grid Locator Completed", exit=False)

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

components = [Label("Select Parameter"),
              ComboBox("Parametros", parametros_dic),Label("Insert Suffix"), TextBox("Sufijo"),
              CheckBox("IncludeDistance","Include Distance"),
              Separator(), Button("Select")]

form = FlexForm("Grid Locator - Select Options", components)
form.show()
# values
if not form.values:
    forms.alert("Options no choosen. Please try again",
                title = "OMBIM_AUTOMATION - Grid Locator",
                exitscript=True)
parameter_selected = form.values["Parametros"]
include_distance = form.values["IncludeDistance"]
sufijo = form.values["Sufijo"]



### UI 2.2 - LOCATIONS POINTS ###
locaciones = GetLocation(element_filters)

### UI 2.3 - GRIDS ####
grids = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_Grids).WhereElementIsNotElementType().ToElements()
grids_horizontal = grid_vertical_horizontal(grids)[0]
grids_vertical= grid_vertical_horizontal(grids)[1]
distances = get_names_and_distances(locaciones, grids_horizontal, grids_vertical, include_distance= include_distance)

### CODE ASIGN ELEMENTS ##


t = Transaction(doc, "Assign Grid Location")
t.Start()

for element, distance in zip(element_filters, distances):

    try:
        parameter = element.LookupParameter(parameter_selected.Definition.Name)

        if parameter and not parameter.IsReadOnly:

            value = "{}{} - {}".format(sufijo,distance[0],distance[1])

            parameter.Set(value)

    except Exception as e:

        print("ERROR ELEMENT {}".format(element.Id))
        print(e)

t.Commit()
message_final(element_filters)