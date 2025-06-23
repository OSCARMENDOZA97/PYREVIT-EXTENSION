# -*- coding: utf-8 -*-

# Imports

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *

# Variables
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument
selection = uidoc.Selection  # type:Selection

app = __revit__.Application  # Application class

rvt_year = int(app.VersionNumber)


def convert_internal_units(length, get_internal=True, units='m'):
    # type: (float,bool) -> float
    """
    Function to convert internal units
    :param units:
    :param length:       Value to convert
    :param get_internal: True to get internal units
    :return:             Lenght in internal units or reverse
    """
    if rvt_year >= 2021:
        from Autodesk.Revit.DB import UnitTypeId
        if   units == 'm' : units = UnitTypeId.Meters
        elif units == 'm2': units = UnitTypeId.SquareMeters
        elif units == 'm3': units = UnitTypeId.CubicMeters
        elif units == 'cm': units = UnitTypeId.Centimeters

    else:
        from Autodesk.Revit.DB import DisplayUnitType
        if   units == 'm' : units = DisplayUnitType.DUT_METERS
        elif units == 'm2': units = DisplayUnitType.DUT_SQUARE_METERS
        elif units == 'm3': units = DisplayUnitType.DUT_CUBIC_METERS
        elif units == 'cm': units = DisplayUnitType.DUT_CENTIMETERS
    if get_internal:
        return UnitUtils.ConvertToInternalUnits(length, units)  # Internas de revit
    return UnitUtils.ConvertFromInternalUnits(length, units)  # Externas de otro archivo


def get_category(item):
    objtype = item.GetType().ToString()
    return_ID = None
    if objtype == "Autodesk.Revit.DB.ViewSchedule":
        return_ID = item.Definition.CategoryId
    elif objtype == "Autodesk.Revit.DB.Family":
        return_ID = item.FamilyCategoryId
    elif objtype == "Autodesk.Revit.DB.GraphicsStyle":
        return_ID = item.GraphicsStyleCategory.Id
    elif objtype == "Autodesk.Revit.DB.Category":
        if item.Parent: return_ID = item.Parent.Id
    elif hasattr(item, "Category"):
        return_ID = item.Category.Id
    if return_ID:
        try:
            return Revit.Elements.Category.ById(return_ID.IntegerValue)
        except:
            return None
    else:
        return None
