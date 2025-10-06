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

from logging import Filter

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

## UI ##
# 1. Collect schedules

selected_schedules = forms.select_schedules(title ="OMBIM_AUTOMATION- Export schedules")
#Case 1- not select schedule
if not selected_schedules:
    forms.alert("Schedule not chosen. Please try again",
                title = "OMBIM_AUTOMATION - Export Schedules",
                exitscript=True)
#Case 2- schedule exceed 31 characters
schedules_exceed = []
for x in selected_schedules:
    schedule_name = Element.Name.GetValue(x)
    if len(schedule_name) > 31:
        schedules_exceed.append(x)
    else:
        pass
if schedules_exceed:
    msg = ("\n⚠ List of schedules exceeds the 31 characters allowed:")
    msg += "\n".join("\n- {}".format(Element.Name.GetValue(x)) for x in schedules_exceed)
    forms.alert(
        msg,
        title = "OMBIM_Automation - Error Name Schedules",
        exitscript=True)

# 2. Select Excel File
file_path = select_file( 'Excel File (*.xlsx)|*.xlsx',"OMBIM_AUTOMATION - Select Excel File")

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

### CODE ###

dictionary_data = get_data_schedules(selected_schedules)
dump(file_path, dictionary_data)

## REPORT FINAL##
names = dictionary_data.keys()

msg = ("  Successfull export schedules ✅\n")
msg += "\n  Total schedules export 📦: {}\n".format(len(names))
msg += "\n  List of schedules export 📃:\n"
msg += "\n".join("    -{}".format(x)for x in names)

Alert(msg, title="OMBIM-AUTOMATION", header="Complete clean Parameters", exit=False)