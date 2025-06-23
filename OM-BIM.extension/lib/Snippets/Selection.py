# -*- coding: utf-8 -*-

# Imports

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *

# Variables
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
selection = uidoc.Selection  # type:Selection

app = __revit__.Application  # Application class

rvt_year = int(app.VersionNumber)


# Funciones

def get_selected_elements():
    """Funcion que permite seleccionar elementos en REVIT."""
    return [doc.GetElement(e_id) for e_id in uidoc.Selection.GetElementIds()]


# Forma larga
"""def get_select_elements(uidoc):
    Funcion que selecciona los elementos en el REVITUI
    doc= uidoc.Document
    print(doc.Title)
    return [doc.GetElement(e_id) for e_id in uidoc.Selection.GetElementIds()]
    """


# ISelectionFilter
# Definir la clase de filtro de selección
class ISelectionFilter_Classes(ISelectionFilter):  # public class == class Method
    def __init__(self, allowed_types):  # Guarda las lista de types permitidas (""" +  enter / control + j)
        """ IselectionFilter made to filter with Types
        \n Input: List of Types
        :param allowed_types:
        """
        self.allowed_types = allowed_types

    def AllowElement(self, element):  # public bool == def Siempre que hay un element se coloca un self
        if type(element) in self.allowed_types:  # CLASES
            return True


class ISelectionFilter_Categories(ISelectionFilter):  # public class == class Method
    def __init__(self, allowed_categories):  # Guarda las lista de categories permitidas (Control +J)
        """ IselectionFilter made to filter with Categories
        \n Input: List of categories
        :param allowed_categories:
        """
        self.allowed_categories = allowed_categories

    def AllowElement(self, element):  # public bool == def Siempre que hay un element se coloca un self
        if element.Category.BuiltInCategory in self.allowed_categories:
            return True


class CustomFilter(ISelectionFilter):  # public class == class Method
    def AllowElement(self, element):  # public bool == def Siempre que hay una clase se coloca un self
        """ IselectionFilter with One categories
        \n Input: Elemento (Tipo)
        :param element:
        :return:
        """
        if element.Category.BuiltInCategory == BuiltInCategory.OST_Rooms:  # Para evitar hacer condicionales
            return True
        return False
