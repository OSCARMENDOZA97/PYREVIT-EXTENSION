# -*- coding: utf-8 -*-
__title__     = "SchedExport"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 1.0
Date    = 20.06.2025
_____________________________________________________________________
Description:
Export data to schedules
_____________________________________________________________________
How-to:
-> Run the script
-> Select Schedules to export
_____________________________________________________________________
Last update:
- [20.06.25] - 1.0 RELEASE
________________________________________________________________________
Author: Oscar Mendoza"""  # Descripcion

### EXTRA: Tu puedes borrar esto
__helpurl__ = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
__min_revit_ver__ = 2021
__max_revit_ver__ = 2025

from distutils.dep_util import newer

# ⬇️ IMPORTS
#--------------------------------------------------------------------------
from Autodesk.Revit.DB import *
from pyrevit import forms
from rpw.ui.forms import *
import xlsxwriter


#📦VARIABLES
#--------------------------------------------------------------------------
uidoc = __revit__.ActiveUIDocument   #type: Document
doc = __revit__.ActiveUIDocument.Document
selection = uidoc.Selection         #type: Selection

# 💻MAIN
#--------------------------------------------------------------------------
#### FUNCTIONS ######
def get_data_schedules(list_schedules):
    """Collect data from schedule
    :list_schedules: List of schedules elements
    :return: Dictionary {schedule_name: table_data}
    """
    result ={}
    for schedule in list_schedules:
        table = schedule.GetTableData().GetSectionData(SectionType.Body)
        schedule_name = Element.Name.GetValue(schedule) #Value x Value
        nRows = table.NumberOfRows  # Family Size Table
        nColumns = table.NumberOfColumns
        #Collect data
        dataListRow = []
        for row in range(nRows):
            dataListColum = []
            for column in range(nColumns):
                dataListColum.append(TableView.GetCellText(schedule, SectionType.Body,row, column ))
            dataListRow.append(dataListColum)
        result[schedule_name] = dataListRow

    return result
#*** FUNCTION  FROM PYREVIT***
def dump(xlfile, datadict):
    """Write data to Excel file.

    Creates a worksheet for each item of the input dictionary.

    Args:
        xlfile (str): full path of the target excel file
        datadict (dict[str, list]): dictionary of worksheets names and data
    """
    xlwb = xlsxwriter.Workbook(xlfile)
    # bold = xlwb.add_format({'bold': True})
    for xlsheetname, xlsheetdata in datadict.items():
        xlsheet = xlwb.add_worksheet(xlsheetname)
        for idx, data in enumerate(xlsheetdata):
            xlsheet.write_row(idx, 0, data)
    xlwb.close()
#*** FUNCTION  TO CHECK SCHEDULES**
def check_schedule_names(list1):
    schedules_exceed = [
        x for x in list1
        if len(Element.Name.GetValue(x)) > 31]

    if schedules_exceed:
        msg = "⚠ The following schedules exceed the 31-character limit:\n"
        msg += "\n".join("- {}".format(Element.Name.GetValue(x)) for x in schedules_exceed)
        msg += "\n\nPlease select Option 2 or Option 3."

        forms.alert(
            msg,
            title="OMBIM_Automation - Schedule Name Error",
            exitscript=True
        )

    return schedules_exceed

### FUNCTION TO MESSAGE ##
def messagefinal(names):
    msg = ("  Successfull export schedules ✅\n")
    msg += "\n  Total schedules export 📦: {}\n".format(len(names))
    msg += "\n  List of schedules export 📃:\n"
    msg += "\n".join("    -{}".format(x) for x in names)

    Alert(msg, title="OMBIM-AUTOMATION", header="Complete export Excel", exit=False)

## UI ##
# 1. Collect schedules

selected_schedules = forms.select_schedules(title ="OMBIM_AUTOMATION- Export schedules")
if not selected_schedules:
    forms.alert("Schedule not chosen. Please try again",
                title = "OMBIM_AUTOMATION - Export Schedules",
                exitscript=True)
# 2. Select Excel File
file_path = select_file( 'Excel File (*.xlsx)|*.xlsx',"OMBIM_AUTOMATION - Select Excel File")

if not file_path:
    forms.alert("ExcelFile not chosen. Please try again",
                title = "OMBIM_AUTOMATION - Export Schedules",
                exitscript=True)
## 3. Select option to export
components = [Label("Select option to Export Excel: "),
              ComboBox("Combobox1",{"Option 1":"OPT1", "Option 2":"OPT2","Option 3":"OPT3"}),

              Label("Option 1: One schedule per sheet, original names."),
              Label("Option 2: One schedule per sheet, assigned names."),
              Label("Option 3: All schedules in a single sheet."),
              Separator(),
              Button("Select")]


form = FlexForm("OMBIM-Export Schedules", components)
form.show()

select_option = form.values
result = select_option.values()[0]

if result == "OPT1":
    check_schedule_names(selected_schedules)
    dictionary_data = get_data_schedules(selected_schedules)
    dump(file_path, dictionary_data)
    ## REPORT FINAL##
    names = dictionary_data.keys()
    messagefinal(names)

if result == "OPT2":
    dictionary_data = get_data_schedules(selected_schedules)
    ### NEW NAMES ###
    names = dictionary_data.keys()
    new_names = ["Excel{}".format(i + 1) for i, _ in enumerate(names)]
    for x,y in zip(names, new_names):
        dictionary_data[y] = dictionary_data.pop(x)
    ## WRITE EXCEL ###
    dump(file_path, dictionary_data)
    ## REPORT FINAL##
    names = dictionary_data.keys()
    messagefinal(names)

if result == "OPT3":
    dictionary_data = get_data_schedules(selected_schedules)
    new_data = []
    for schedule_name, schedule_data in dictionary_data.items():
        new_data.append([schedule_name])   # Título del schedule
        new_data.extend(schedule_data)     # Filas del schedule
        new_data.append([])                # Fila vacía como separador
    new_dictionary = {}
    new_dictionary["ExcelResume"] = new_data
    ## WRITE EXCEL ###
    dump(file_path, new_dictionary)
    ## REPORT FINAL##
    names = dictionary_data.keys()
    messagefinal(names)






