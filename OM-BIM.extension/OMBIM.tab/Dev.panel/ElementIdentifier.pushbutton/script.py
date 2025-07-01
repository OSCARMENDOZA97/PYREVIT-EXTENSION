# -*- coding: utf-8 -*-
__title__     = "ElemID"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 1.0
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
________________________________________________________________________
Author: Oscar Mendoza"""  # Descripcion

### EXTRA: Tu puedes borrar esto
__helpurl__ = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# ⬇️ IMPORTS
#--------------------------------------------------------------------------
import Autodesk
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms
from Snippets._params import *
from rpw.ui.forms import *
#📦VARIABLES
#--------------------------------------------------------------------------
uidoc = __revit__.ActiveUIDocument   #type: Document
doc = __revit__.ActiveUIDocument.Document
selection = uidoc.Selection         #type: Selection

# 💻MAIN
#--------------------------------------------------------------------------
## FUNCTIONS ## #
def collection_for_name_category(nombre=None):
    """
    Uso:
        Selecciona una o varias categorías de revit por nombre
    Entradas:
        nombre <str> o <list[str]>: Nombre(s) de categoría(s) a seleccionar.
        Si es None, devuelve la lista completa de nombres de categorías.
    Salida:
        Si se introduce correctamente el nombre, se obtiene un diccionario con los nombres
        y categorías correspondientes
    """
    #Acceder al listado completo categorías
    categories = doc.Settings.Categories
    names = [cat.Name for cat in categories]
    dic_categories = dict(zip(names, categories))
    if nombre:
        #Case 1 : Str
        if isinstance(nombre, str):
            if nombre in names:
                salida = {nombre :dic_categories[nombre]} # dict one element
            else:
                salida = "Check name"
        #Case2 : List
        if isinstance(nombre, list):
            for x in nombre:
                if x in names:
                    salida = {n: dic_categories[n] for n in nombre if n in dic_categories.keys()} #dict two or more
                else:
                    salida = "Check name"
    else:
        salida = sorted(names)
    return salida

def collect_elements_category(cats, instance = True):
    """
    Uso:
        Seleccionar todos los elementos por categoría
    Entrada:
        Cat <Autodesk.Revit.DB.Category>:Categoría o Categorias
    Salida:
        Se genera un diccionario separando instancias y tipos
    """
    Instances = []
    Types = []
    for x in cats:
        if isinstance(x, Category):
            colection = FilteredElementCollector(doc).OfCategoryId(x.Id).ToElements()
            # Pregunta a cada elemento por el id de su tipo si el elemento se trata de
            # un tipo nos dara un -1 si es instancia obtendremos un id valido
            for ele in colection:
                if ele.GetTypeId() == ElementId.InvalidElementId:
                    Types.append(ele)
                else:
                    Instances.append(ele)
        else:
            print("Aviso'{x}'".format("No es un objeto Category"))
    if instance:
        return Instances
    else:
        return Types
def collect_params():
    """Check if any parameters from provided list are missing in the project
    :dicc boolean:
    :return: dictionary name:element
    """
    # Get Parameter Bindings Map. - Mapa de enlaces de parámetros
    bm = doc.ParameterBindings

    # Create a forward iterator
    itor = bm.ForwardIterator()
    itor.Reset()

    # Iterate over the map - class external definition
    loaded_parameters_dic = {}
    while itor.MoveNext():
        try:
            elem = doc.GetElement(itor.Key.Id)
            d = itor.Key  # type: Definition
            loaded_parameters_dic[d.Name] = d.Name   # clave: Definition, su nombre: su nombre
        except:
            pass
    return loaded_parameters_dic
### CODE #####
# CATEGORIES
list_categories_names=get_category().keys() # Collect categories PEB
list_categories = collection_for_name_category(nombre=list_categories_names) # CATEGORIES FOR NAME
salida = collect_elements_category(list_categories.values(), instance = True) # INSTANCES
# COLLECT PARAMS
params = collect_params()

### UI ###
components = [Label("ID Param"), ComboBox("ID", params),
              CheckBox("ID_Param", "Set ElementID?"),
              Label("UniqueId Param"), ComboBox("UniqueID", params),
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
        for x in salida:
            param = x.LookupParameter(param_ID)
            if param is not None:
                param.Set(str(x.Id))
        t.Commit()
    msg = ("✅ Successfully assigned Element ID to elements.\n")
    msg += "📦 Total elements processed: {}\n".format(len(salida))
    Alert(msg, title="OMBIM | Element Identifier", header="Element ID assignment complete", exit=False)
## CASE 3 UNIQUE_ID

if UniqueID_filter:
    with Transaction(doc, "Set OM_UNIQUEID_BIM") as t:
        t.Start()
        for x in salida:
            param = x.LookupParameter(param_uniqueID)
            if param is not None:
                param.Set(str(x.UniqueId))
        t.Commit()
    msg = ("✅ Successfully assigned Unique ID to elements.\n")
    msg += "📦 Total elements processed: {}\n".format(len(salida))
    Alert(msg, title="OMBIM | Element Identifier", header="Unique ID assignment complete", exit=False)