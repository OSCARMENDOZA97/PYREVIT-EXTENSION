# -*- coding: utf-8 -*-
__title__     = "ExcelSheets"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 1.0
Description:
Create Revit Sheets automatically from an Excel file.
The script reads sheet data (number, name, template, etc.)
and generates new sheets in the active Revit project.

_____________________________________________________________________
How-to:
-> Run the script
-> Select the Excel file containing sheet data
-> Map columns (e.g., Sheet Number, Sheet Name)
-> Confirm creation to generate the sheets automatically
_____________________________________________________________________
Last update:
- [05.10.2025] - 1.0 RELEASE
- [05.10.2025] - Added Excel column validation
_____________________________________________________________________
Author: Oscar Mendoza"""  # Descripcion

### EXTRA: Tú puedes borrar esto
__helpurl__ = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

from csv import excel

# ⬇️ IMPORTS
#--------------------------------------------------------------------------
#IMPORTS ⬇️
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import UIApplication
from pyrevit import forms   # By importing forms you also get references to WPF package! IT'S Very IMPORTANT !!!
import wpf, clr , sys        # wpf can be imported only after pyrevit.forms!
import os # noinspection PyUnusedImport
from pyrevit import revit,HOST_APP
from rpw.ui.forms import *



# .NET Imports ✈️
clr.AddReference("System")
from System.Collections.Generic import List
from System.Windows import *
from System.Windows.Controls import CheckBox, Button, TextBox, ListBoxItem, TextBlock, ComboBoxItem
from System import Uri

import xlrd

#📦VARIABLES
#--------------------------------------------------------------------------
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
PATH_SCRIPT = os.path.dirname(__file__) # Dirección actual

# 💻MAIN
#--------------------------------------------------------------------------

# Functions


def excel_to_rows(filepath, index):
    workbook = xlrd.open_workbook(file_path)
    sheet = workbook.sheet_by_index(int(index))

    row_count = sheet.nrows
    col_count = sheet.ncols

    data_all = []

    for row in range(0, row_count):
        data = [] # Creamos una lista para cada fila
        for col in range(0,col_count):
            data.append(sheet.cell_value(row,col))
        data_all.append(data)

    return data_all


#Element.Name.GetValue(x)

excel_path = None  # Variable global para guardar la ruta

#MAIN FORM💻
# Inherit .NET Window for your UI Form Class
class FirstButton(Window):
    def __init__(self):
        # Connect to .xaml File (in the same folder!) -
        path_xaml_file = os.path.join(PATH_SCRIPT, 'BaseUI.xaml')
        wpf.LoadComponent(self, path_xaml_file)

        # Populate Combobox with types()
        self.populate_combobox_with_TitleBlock()

        # Show Form
        self.ShowDialog()


    def populate_combobox_with_TitleBlock(self):
        # Global Variables
        title_types = FilteredElementCollector(doc).OfCategory(BuiltInCategory.OST_TitleBlocks).WhereElementIsElementType().ToElements()
        dic_titles = {Element.Name.GetValue(typ): typ for typ in title_types}

        # Clear combobox
        self.UI_combobox.Items.Clear()

        #Populate new items
        for title_block_name , titleblock_type in dic_titles.items():
            # Create Combobox items
            comboBoxItem         = ComboBoxItem()
            comboBoxItem.Content = title_block_name
            comboBoxItem.Tag     = titleblock_type.Id

            # Add ComboboxItem to combobox
            self.UI_combobox.Items.Add(comboBoxItem)

        # Select first item
        self.UI_combobox.SelectedIndex = 0

    # Property 🧬
    @property
    def combobox_item(self):
        return self.UI_combobox.SelectedItem.Tag

    @property
    def textbox_item(self):
        return self.UI_text.Text


    def UI_Browse(self, sender, e):
        global excel_path
        excel_path = forms.pick_file(file_ext='xlsx',
                                     init_dir='D:\\',
                                     title='Select Excel File')
        if excel_path:
            self.UI_FilePath.Text = excel_path
    # Events
    def Close_Click(self, sender, e):
        self.Close()

# Show form to the user
UI = FirstButton()

## ERRORS ##
if not excel_path:
    forms.alert(
        "Please select an Excel file before continuing.",
        title="OMTools | Excel Sheets",exitscript=True)

## CODE ####
else:
    title_block_type = UI.combobox_item
    file_path        = excel_path
    data_excel       = excel_to_rows(file_path,UI.textbox_item)
    with Transaction(doc, "Create New Sheet") as t:
        t.Start()
        for lf in data_excel:
            View_Sheet = ViewSheet.Create(doc, title_block_type)  # Creacion Planos
            View_Sheet.SheetNumber = lf[0]
            View_Sheet.Name = lf[1]
        t.Commit()
    msg = "✅ Sheets created successfully in Revit.\n"
    msg += "📄 Total sheets generated: {}\n".format(len(data_excel))
    msg += "\nAll sheets were created based on the selected Excel file."

    Alert(
        msg,
        title="OMTools | Excel Sheets",
        header="Sheet Creation Complete",
        exit=False)