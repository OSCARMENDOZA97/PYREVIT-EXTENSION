# -*- coding: utf-8 -*-
__title__     = "Plantilla_Pyrevit"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 1.0
Date    = 21.12.2023
_____________________________________________________________________
Description:
Select Linked Elements based on selected in UI:
- Revit Linked Project
- Element Categories 
_____________________________________________________________________
How-to:
-> Run the script
-> Select Linked Revit Project
-> Select Revit Categories
-> Pick Linked Elements matching selected criteria
_____________________________________________________________________
Last update:
- [21.12.2023] - 1.0 RELEASE
- [21.02.2025] - 1.1 BuiltinCategory Invalid
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

#📦VARIABLES
#--------------------------------------------------------------------------
uidoc = __revit__.ActiveUIDocument   #type: Document
doc = __revit__.ActiveUIDocument.Document
selection = uidoc.Selection         #type: Selection

# 💻MAIN
#--------------------------------------------------------------------------



