# -*- coding: utf-8 -*-
__title__ = "RoomDataTransfer"
__author__ = "Oscar Mendoza"
__doc__ = """Version = 3.0
Date    = 26.05.2026
_____________________________________________________________________
Description:
Identifies rooms within either the host model (native) or a linked 
Architecture model, and automatically assigns a user-selected Room 
parameter into a user-selected Element parameter.
Supports point-based, curve-based, and solid-based (Floors) elements.
_____________________________________________________________________
How-to:
-> Run the script.
-> Select the categories to analyze.
-> Select either the Local Model or a Linked instance from the UI.
-> Select the source Room parameter and the target Element parameter.
_____________________________________________________________________
Last update:
- [26.05.2026] - 3.0 Dynamic Room Parameter extraction UI added"""

__helpurl__ = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
__min_revit_ver__ = 2021
__max_revit_ver__ = 2027

# ⬇️ IMPORTS
# --------------------------------------------------------------------------
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
import System
from pyrevit import forms, revit, script
from rpw.ui.forms import *

# 📦 GLOBAL VARIABLES & DOCUMENT
# --------------------------------------------------------------------------
doc = revit.doc

BUILT_IN_CATEGORIES = ["OST_ShaftOpening", "OST_DuctAccessory", "OST_PipeAccessory", "OST_Coupler",
                       "OST_VibrationManagement", "OST_DuctInsulations", "OST_PipeInsulations", "OST_DuctLinings",
                       "OST_ElectricalFixtures", "OST_PlumbingFixtures", "OST_Parking", "OST_Areas", "OST_FabricAreas",
                       "OST_Rebar", "OST_MEPAnalyticalFraming", "OST_StructuralFraming", "OST_CableTray",
                       "OST_StairsRailing", "OST_MEPAnalyticalBus", "OST_Wire",
                       "OST_StructuralTendon", "OST_BridgeCables", "OST_MechanicalEquipment", "OST_Roads",
                       "OST_StructuralFoundation", "OST_MEPAnalyticalWaterLoop", "OST_ElectricalCircuit",
                       "OST_VerticalCirculation", "OST_DuctCurves", "OST_FlexDuctCurves", "OST_ElectricalLoadSet",
                       "OST_MechanicalEquipmentSet", "OST_BridgeAbutments", "OST_Roofs", "OST_AudioVisualDevices",
                       "OST_FireAlarmDevices", "OST_CommunicationDevices", "OST_MechanicalControlDevices",
                       "OST_DataDevices",
                       "OST_LightingDevices", "OST_SecurityDevices", "OST_TelephoneDevices", "OST_Site",
                       "OST_Entourage", "OST_PlumbingEquipment", "OST_FoodServiceEquipment", "OST_ZoneEquipment",
                       "OST_Railing", "OST_CableConduit", "OST_ElectricalEquipment", "OST_SpecialityEquipment",
                       "OST_MechanicalEquipment", "OST_Stairs", "OST_BridgeFraming", "OST_TemporaryStructure",
                       "OST_RebarShape", "OST_ElectricalPowerSource",
                       "OST_MEPAnalyticalTransferSwitch", "OST_ExpansionJoints", "OST_LightingFixtures",
                       "OST_FabricReinforcement", "OST_PlaceHolderDucts", "OST_PlaceHolderPipes", "OST_Mass",
                       "OST_Furniture", "OST_GenericModel", "OST_Casework", "OST_Walls", "OST_Hardscape", "OST_Parts",
                       "OST_StructuralColumns", "OST_BridgePiers", "OST_Bearings", "OST_FireProtection",
                       "OST_Doors", "OST_Ramps", "OST_FabricationDuctwork", "OST_AreaRain", "OST_PathRein",
                       "OST_CurtainGrids", "OST_SwitchSystem", "OST_FabricationDuctworkStiffeners",
                       "OST_StructuralStiffener", "OST_Sprinklers", "OST_Signage", "OST_MEPAnalyticalLoad",
                       "OST_Curtains", "OST_FabricationHangers",
                       "OST_Floors", "OST_BridgeDecks", "OST_Ceilings", "OST_DuctTerminal", "OST_NurseCallDevices",
                       "OST_CableTrayRun", "OST_ConduitRun", "OST_ElectricalAnalyticalTransformer", "OST_PipeCurves",
                       "OST_FabricationPipework", "OST_FlexPipeCurves", "OST_Conduit", "OST_CableTrayFitting",
                       "OST_DuctFitting", "OST_PipeFitting", "OST_ConduitFitting", "OST_Planting", "OST_Windows",
                       "OST_StructuralTruss"]


# 🛠️ HELPER FUNCTIONS
# --------------------------------------------------------------------------

def collect_elements(target_doc, list_bic):
    """Collects all model elements matching the provided list of categories."""
    elements = []
    for name in list_bic:
        try:
            bic_enum = System.Enum.Parse(BuiltInCategory, name)
            collected = FilteredElementCollector(target_doc).OfCategory(bic_enum).WhereElementIsNotElementType().ToElements()
            if collected:
                elements.extend(list(collected))
        except:
            pass
    return elements


def get_category_names(list_elements):
    """Returns sorted unique category names present in the retrieved elements."""
    return sorted(list(set([x.Category.Name for x in list_elements if x.Category])))


def get_common_parameters(elements):
    """Finds common, editable String parameters across the selected elements."""
    if not elements:
        return []

    parameters_name = set([p.Definition.Name for p in elements[0].Parameters])

    for element in elements[1:]:
        element_params = set([p.Definition.Name for p in element.Parameters])
        parameters_name.intersection_update(element_params)

    valid_parameters = [
        p for p in elements[0].Parameters
        if p.Definition.Name in parameters_name
           and p.StorageType == StorageType.String
           and not p.IsReadOnly
    ]
    return valid_parameters


def get_room_parameters(target_doc):
    """Retrieves readable string-based parameters from rooms in the target document."""
    rooms = FilteredElementCollector(target_doc) \
        .OfCategory(BuiltInCategory.OST_Rooms) \
        .WhereElementIsNotElementType() \
        .ToElements()

    valid_rooms = [r for r in rooms if r.Area > 0]

    if not valid_rooms:
        return []

    # Extract parameters from the first valid room sample found
    sample_room = valid_rooms[0]
    valid_room_params = [
        p for p in sample_room.Parameters
        if p.StorageType == StorageType.String or p.Definition.Name in ["Number", "Name"]
    ]
    return valid_room_params


def get_location_point(element):
    """Extracts the optimal geometric point based on the element's Location type."""
    location = element.Location

    if isinstance(location, LocationPoint):
        return location.Point

    elif isinstance(location, LocationCurve):
        return location.Curve.Evaluate(0.5, True)

    else:
        try:
            bbox = element.get_BoundingBox(None)
            if bbox:
                min_p = bbox.Min
                max_p = bbox.Max
                mid_x = (min_p.X + max_p.X) / 2.0
                mid_y = (min_p.Y + max_p.Y) / 2.0
                mid_z = (min_p.Z + max_p.Z) / 2.0
                return XYZ(mid_x, mid_y, mid_z)
        except:
            pass

    return None


def validate_rooms_in_document(target_doc):
    """Validates if there are placed rooms with an area greater than 0 in the target document."""
    if not target_doc:
        return False
    rooms = FilteredElementCollector(target_doc) \
        .OfCategory(BuiltInCategory.OST_Rooms) \
        .WhereElementIsNotElementType() \
        .ToElements()
    valid_rooms = [r for r in rooms if r.Area > 0]
    return len(valid_rooms) > 0


# 🚀 MAIN EXECUTION
# --------------------------------------------------------------------------
def main():
    # 1. Initial collection of local elements
    all_elements = collect_elements(doc, BUILT_IN_CATEGORIES)
    if not all_elements:
        forms.alert("No elements were found in the configured categories.", title="Collection Error")
        script.exit()

    # 2. UI 1: Select Local Categories
    available_categories = get_category_names(all_elements)
    selected_categories = forms.SelectFromList.show(
        available_categories,
        title="Room Locator - Select Categories",
        button_name="Next",
        multiselect=True)

    if not selected_categories:
        script.exit()

    filtered_elements = [x for x in all_elements if x.Category.Name in selected_categories]

    # 3. UI 2: Common parameters from local elements
    common_parameters = get_common_parameters(filtered_elements)
    if not common_parameters:
        forms.alert("No editable, string-type common parameters were found in the local elements.",
                    title="Parameter Error")
        script.exit()

    param_elements_dic = {p.Definition.Name: p for p in common_parameters}

    # 4. UI 3: Select Source Model (Native Model or Links)
    LOCAL_MODEL_KEY = "-> LOCAL MODEL (NATIVE)"
    sources_dic = {LOCAL_MODEL_KEY: doc}

    link_instances = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()
    for link in link_instances:
        sources_dic[link.Name] = link

    selected_source_key = SelectFromList("Select the Source Model containing the Rooms",
        sources_dic.keys())

    if not selected_source_key:
        script.exit()

    # Determine document database based on selection to retrieve Rooms
    is_local_model = (selected_source_key == LOCAL_MODEL_KEY)
    if is_local_model:
        room_doc = doc
        link_transform = None
    else:
        selected_link_instance = sources_dic[selected_source_key]
        room_doc = selected_link_instance.GetLinkDocument()
        link_transform = selected_link_instance.GetTotalTransform()

    # Validate that rooms exist in the selected destination
    if not validate_rooms_in_document(room_doc):
        forms.alert(
            "The selected source does NOT contain valid or placed rooms.",
            title="Room Validation Failed",
            warn_icon=True)
        script.exit()

    # 5. Extract dynamic parameters from source Room
    room_parameters = get_room_parameters(room_doc)
    if not room_parameters:
        forms.alert("Could not read text parameters from the rooms in the source model.", title="Error")
        script.exit()

    param_rooms_dic = {p.Definition.Name: p for p in room_parameters}

    # 6. UI 4: Parameter mapping form (Source Room -> Target Element)
    components = [
        Label("Extract parameter from Room (Source):"),
        ComboBox("RoomParameter", sorted(param_rooms_dic.keys())),
        Separator(),
        Label("Write into Element parameter (Target):"),
        ComboBox("ElementParameter", sorted(param_elements_dic.keys())),
        Separator(),
        Button("Submit")
    ]

    form = FlexForm("Room Locator - Parameter Mapping", components)
    form.show()

    if not form.values:
        script.exit()

    room_param_name = form.values["RoomParameter"]
    element_param_name = form.values["ElementParameter"]

    # 7. Transaction and Dynamic Data Assignment
    counter = 0

    with Transaction(doc, "Assign Room Parameter") as t:
        t.Start()

        for element in filtered_elements:
            point = get_location_point(element)

            if point:
                if isinstance(element.Location, LocationPoint):
                    point = XYZ(point.X, point.Y, point.Z + 0.7)
                # If it's a link, invert coordinates. If local, use directly.
                analysis_point = link_transform.Inverse.OfPoint(point) if not is_local_model else point
                # Geometrically detect Room
                room = room_doc.GetRoomAtPoint(analysis_point)

                if room:
                    # Dynamically extract selected parameter from Room
                    p_room = room.LookupParameter(room_param_name)
                    value_to_set = ""

                    if p_room:
                        value_to_set = p_room.AsString() if p_room.StorageType == StorageType.String else p_room.AsValueString()

                    if not value_to_set:
                        value_to_set = room.get_Parameter(BuiltInParameter.ROOM_NUMBER).AsString() if room_param_name == "Number" else ""

                    parameter = element.LookupParameter(element_param_name)

                    if parameter and not parameter.IsReadOnly and value_to_set:
                        parameter.Set(value_to_set)
                        counter += 1

        t.Commit()

    # 8. Final Results Output
    output = script.get_output()
    output.print_md("### **Process Completed Successfully**")
    output.print_md("Rooms analyzed from: **{}**".format(selected_source_key))
    output.print_md(
        "Mapping completed: Room [**`{}`**] -> Element [**`{}`**]".format(room_param_name, element_param_name))
    output.print_md("Successfully updated **{}** elements.".format(counter))


if __name__ == "__main__":
    main()
