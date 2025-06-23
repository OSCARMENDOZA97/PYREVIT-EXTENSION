# -*- coding: utf-8 -*-
__title__     = "AddParams"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 1.1
Date    = 04.06.2025
_____________________________________________________________________
Description:
Create Project Parameters from txt Shared Parameters
Last update:
- [03.06.2025] - 1.0 RELEASE
________________________________________________________________________
Author: Oscar Mendoza"""  # Descripcion

### EXTRA: Tu puedes borrar esto
__helpurl__ = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

# ⬇️ IMPORTS
#--------------------------------------------------------------------------
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms
from rpw.ui.forms import SelectFromList, Alert
from Snippets._params import *

#📦VARIABLES
#--------------------------------------------------------------------------
uidoc = __revit__.ActiveUIDocument   #type: Document
doc = __revit__.ActiveUIDocument.Document
selection = uidoc.Selection         #type: Selection
app = __revit__.Application

# 💻MAIN
#--------------------------------------------------------------------------

def get_shared_params_by_group(group_name = True):
    """Collect shared parameters from txt filtered by group
    :param group_name:
        True  -> Returns dictionary {GroupName: [ParameterNames]}
        False -> Returns dictionary {ParameterName: DefinitionObject}
    :return: Dictionary based on mode
    """
    sp_file = app.OpenSharedParameterFile()
    if not sp_file:
        forms.alert("Couldn't find SharedParameterFile"
                    "\nPlease Set the file in Revit and Try Again", exitscript=True)
    shared_parameters_groups = {}
    found_params = {}
    for group in sp_file.Groups: #DefinitionFile
        param_list=[]
        #print('\nGroup Name: {}'.format(group.Name))
        for p_def in group.Definitions:
            param_list.append(p_def.Name)
            shared_parameters_groups[group.Name] = param_list
            found_params[p_def.Name] = p_def
    if group_name:
        return shared_parameters_groups
    else:
        return found_params

shared_group = get_shared_params_by_group(group_name=True)
found_params = get_shared_params_by_group(group_name=False)

#Obtain definitions

#Dropdown - Group
key_group = SelectFromList("Select Group Parameters",
                           get_shared_params_by_group().keys())
#List - Params
value_group = forms.SelectFromList.show((shared_group)[key_group],
                                        title = "OMBIM_AUTOMATION",
                                        multiselect = True,
                                        button_name = "Select Params")

if not  value_group:
    forms.alert("Don't select parameters"
                "\nPlease Set the parameters and Try Again", exitscript=True)

value_definition = [found_params[name] for name in value_group]

#Obtain bic_categories

categories = get_category() # category_dic[cats_name] = cat.BuiltInCategory

categories_ = forms.SelectFromList.show(categories.keys(),
                                        title = "OMBIM_AUTOMATION",
                                        multiselect = True,
                                        button_name = "Select Categories")
if not  categories_:
    forms.alert("Don't select categories"
                "\nPlease Set the categories and Try Again", exitscript=True)

bic_categories = [categories[name] for name in categories_]

#Obtain GroupTypeId
key_group = SelectFromList("Select GroupTypeId",
                           get_parameter_group().keys())
p_group_ = get_parameter_group()[key_group]

def load_params(p_def_to_load,
                bic_cats,
                p_group,
                bind_mode='instance'):
        # type: (list,list, str, GroupTypeId) -> None

    """ Function to check Loaded SharedParameters
    :param p_def_to_load  List of parameter names
    :param  bic_cats:      List of BuiltinCategories for Parameters
    :param p_group:        GroupTypeId
    :param bind_mode:      Binding Mode: 'instance' / 'type'"""
    # Create CategorySet
    cat_set = CategorySet()
    for cat in bic_cats:
        cat_set.Insert(cat)
    # Binding
    binding = InstanceBinding(cat_set) if bind_mode == 'instance' else TypeBinding(cat_set)

    # Add parameters
    for p_def in p_def_to_load:
        doc.ParameterBindings.Insert(p_def, binding, p_group)


t = Transaction(doc, "Create Params")
t.Start()
load_params(value_definition, bic_categories, p_group=p_group_,bind_mode='instance')
t.Commit()
Alert('Create total {} parameters'.format(len(value_definition)), title="OMBIM-AUTOMATION",
              header="Complete create Parameters", exit=False)
