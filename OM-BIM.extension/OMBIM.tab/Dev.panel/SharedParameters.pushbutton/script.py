# -*- coding: utf-8 -*-
__title__     = "LimpiaShared"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 1.1
Date    = 04.06.2025
_____________________________________________________________________
Description:
Shared Parameters 
Last update:
- [03.06.2025] - 1.0 RELEASE
- [04.06.2025] - 1.1 CHANGE METHOD CLEAN
________________________________________________________________________
Author: Oscar Mendoza"""  # Descripcion

# ⬇️ IMPORTS
#--------------------------------------------------------------------------
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
# Import pyrevit libraries
from pyrevit import DB, revit
from pyrevit import forms, script
from rpw.ui.forms import Alert


#📦VARIABLES
#--------------------------------------------------------------------------
uidoc = __revit__.ActiveUIDocument   #type: Document
doc = __revit__.ActiveUIDocument.Document
selection = uidoc.Selection         #type: Selection
app = __revit__.Application

# 💻MAIN
#--------------------------------------------------------------------------
from pyrevit import forms

def check_loaded_params_txt(dicc = True):
    """Check if any parameters from provided list are missing in the project
    :param list_p_names:
    :return:
    """
    sp_file = app.OpenSharedParameterFile()
    if not sp_file:
        forms.alert("Couldn't find SharedParameterFile"
                    "\nPlease Set the file in Revit and Try Again", exitscript=True)
    found_params  = []

    for group in sp_file.Groups: #DefinitionFile
        #print('\nGroup Name: {}'.format(group.Name))
        for p_def in group.Definitions:
            found_params.append(p_def.Name) # REVISAR

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
            loaded_parameters_dic[d.Name] = elem   # clave: Definition, valor: su nombre
        except:
            pass
    if dicc:
        return loaded_parameters_dic
    else:
        missing_params = [d for d in loaded_parameters_dic.keys() if d not in found_params]
        return missing_params

m_params_dic = check_loaded_params_txt(dicc=True)
m_params_name = check_loaded_params_txt(dicc=False)

t = Transaction(doc, "Delete Shared Params3")
t.Start()

t.Commit()
if not m_params_name:
    forms.alert("All project parameters exist and match the shared parameter file.", title= "OMBIM AUTOMATION", exitscript=True)
else:
    m_params_filter = forms.SelectFromList.show(m_params_name,
                                                title="Select Parameters to clean",
                                                width=500,
                                                height=450,
                                                button_name="Select Option",
                                                multiselect=True)
    if not m_params_filter:
        forms.alert("No select parameters. Please try again", title = "OMBIM AUTOMATION", exitscript=True)

    values = [m_params_dic.get(key) for key in m_params_filter if key in m_params_dic]
    if values:
        t = Transaction(doc, "Delete Shared Parameters")
        t.Start()
        for x in values:
            doc.Delete(x.Id)
        t.Commit()

        Alert('Delete total {} parameters'.format(len(values)), title="OMBIM-AUTOMATION",
              header="Complete clean Parameters", exit=False)
    else:
        forms.alert("Not Select Parameters", exitscript=True)
