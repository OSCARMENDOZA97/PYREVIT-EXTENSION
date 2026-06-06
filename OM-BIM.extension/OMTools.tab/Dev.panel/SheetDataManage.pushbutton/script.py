# -*- coding: utf-8 -*-
__title__ = "Sheet MetaData"
__doc__ = """Version = 1.6
Description:
Exports or Imports selected Revit sheets metadata 
and user-selected parameters using an Excel spreadsheet.
_____________________________________________________________________
How-to:
-> Run the script
-> Choose between Export or Import mode via UI
-> Follow the on-screen prompts based on your selection
_____________________________________________________________________
Last update:
- [06.06.2026] - 1.6 Isolated xlrd reading engine into its own load_xlsheet function
Author: Oscar Mendoza"""

__min_revit_ver__ = 2021
__max_revit_ver__ = 2026

# ⬇️ IMPORTS
# --------------------------------------------------------------------------
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms
from rpw.ui.forms import FlexForm, Label, ComboBox, Button
import xlsxwriter
import xlrd

# 📦VARIABLES
# --------------------------------------------------------------------------
uidoc = __revit__.ActiveUIDocument
doc = __revit__.ActiveUIDocument.Document
selection = uidoc.Selection


# 🛠️ HELPER FUNCTIONS
# --------------------------------------------------------------------------
def GetCommonParameters(doc, elementos):
    if not elementos:
        return []

    ignored_bips = [LabelUtils.GetLabelFor(BuiltInParameter.SHEET_NAME),
                    LabelUtils.GetLabelFor(BuiltInParameter.SHEET_NUMBER)]

    first_element_params = [
        p for p in elementos[0].Parameters
        if p.StorageType == StorageType.String
           and not p.IsReadOnly
           and p.Definition.Name not in ignored_bips]

    parametersName = set([p.Definition.Name for p in first_element_params])

    for element in elementos[1:]:
        elementParametersName = set([p.Definition.Name for p in element.Parameters])
        parametersName.intersection_update(elementParametersName)

    final_parameters_dict = {}
    for p in first_element_params:
        if p.Definition.Name in parametersName:
            final_parameters_dict[p.Definition.Name] = p

    return final_parameters_dict


def dump(xlfile, datadict):
    """Write data to Excel file."""
    xlwb = xlsxwriter.Workbook(xlfile)
    bold = xlwb.add_format({'bold': True})

    for xlsheetname, xlsheetdata in datadict.items():
        xlsheet = xlwb.add_worksheet(xlsheetname)
        for idx, data in enumerate(xlsheetdata):
            if idx == 0:
                xlsheet.write_row(idx, 0, data, bold)
            else:
                xlsheet.write_row(idx, 0, data)
    xlwb.close()


def load_xlsheet(xlfile):
    """Read data from Excel file using xlrd.

    Returns:
        tuple: (headers, rows) donde headers es una lista de strings
               y rows es una lista de listas con los valores limpios.
    """
    wb = xlrd.open_workbook(xlfile)
    ws = wb.sheet_by_index(0)  # Lee la primera pestaña por defecto

    # Extraer encabezados de la fila 0
    headers = [ws.cell_value(0, col) for col in range(ws.ncols)]

    # Extraer el resto de filas procesando tipos de datos flotantes de Excel
    rows = []
    for row_idx in range(1, ws.nrows):
        row_data = []
        for col_idx in range(ws.ncols):
            val = ws.cell_value(row_idx, col_idx)

            # Corregir la lectura de números enteros que xlrd transforma a floats (Ej: 101.0 -> "101")
            if isinstance(val, float) and val.is_integer():
                val = str(int(val))
            elif val is None:
                val = ""
            else:
                val = str(val)
            row_data.append(val)
        rows.append(row_data)

    return headers, rows


# 📦 CORE MODULES (MAIN FUNCTIONS)
# --------------------------------------------------------------------------
def ejecutar_exportacion():
    """Process for sheet selection, parameters selection, and exporting to Excel."""
    selected_sheets = forms.select_sheets()
    if not selected_sheets:
        forms.alert("No sheets were selected.", title="OMTools | SheetSync", exitscript=True)

    parametros = GetCommonParameters(doc, selected_sheets)

    parametros_ui = forms.SelectFromList.show(
        sorted(parametros.keys()),
        title="OMTools | Select Parameters to Export",
        multiselect=True,
        button_name="Select Param")

    if not parametros_ui:
        forms.alert("No additional parameters were selected for export.", title="OMTools | SheetSync",
                    exitscript=True)

    excel_path = forms.save_file(file_ext='xlsx', title="Save Sheet Report")
    if not excel_path:
        forms.alert("Operation cancelled by user.", title="OMTools | SheetSync", exitscript=True)

    headers = ["Sheet Number", "Sheet Name"] + parametros_ui
    excel_data = [headers]

    with forms.ProgressBar(title="Exporting sheets...", max_value=len(selected_sheets)) as pb:
        for idx, sheet in enumerate(selected_sheets):
            row = [sheet.SheetNumber, sheet.Name]

            for param_name in parametros_ui:
                p = sheet.LookupParameter(param_name)
                if p and p.HasValue:
                    row.append(p.AsString())
                else:
                    row.append("")
            excel_data.append(row)
            pb.update_progress(idx + 1)

    data_dict = {"Revit Sheets": excel_data}

    try:
        dump(excel_path, data_dict)
        forms.alert("Data successfully exported.\nTotal sheets: {}".format(len(selected_sheets)),
                    title="OMTools | Export Complete", warn_icon=False)
    except Exception as ex:
        forms.alert("Error exporting to Excel: {}".format(str(ex)), title="OMTools | Error")


def ejecutar_importacion():
    """Process for reading Excel data and updating parameters in Revit."""
    excel_path = forms.pick_file(file_ext='xlsx', title="Select Excel File to Import")
    if not excel_path:
        forms.alert("Operation cancelled by user.", title="OMTools | SheetSync", exitscript=True)

    try:
        headers, rows = load_xlsheet(excel_path)

        if "Sheet Number" not in headers:
            forms.alert("The Excel file does not contain the required 'Sheet Number' column.", title="OMTools | Error",
                        exitscript=True)

        idx_number = headers.index("Sheet Number")

        # Sheet Filtering
        all_sheets = FilteredElementCollector(doc).OfClass(ViewSheet).ToElements()
        sheets_dict = {s.SheetNumber: s for s in all_sheets}

        t = Transaction(doc, "OMTools | Import Sheet Data")
        t.Start()

        counter = 0
        total_rows = len(rows)

        if total_rows > 0:
            with forms.ProgressBar(title="Importing and updating sheets...", max_value=total_rows) as pb:
                for idx, row in enumerate(rows):
                    sheet_num = row[idx_number].strip() if row[idx_number] else None

                    if sheet_num and sheet_num in sheets_dict:
                        revit_sheet = sheets_dict[sheet_num]

                        for col_idx, header_name in enumerate(headers):
                            val = row[col_idx]

                            if header_name == "Sheet Number":
                                continue
                            elif header_name == "Sheet Name":
                                revit_sheet.Name = val
                            else:
                                p = revit_sheet.LookupParameter(header_name)
                                if p and not p.IsReadOnly:
                                    p.Set(val)
                        counter += 1
                    pb.update_progress(idx + 1)

        t.Commit()
        forms.alert("Successfully updated {} sheets in Revit.".format(counter),
                    title="OMTools | Import Complete", warn_icon=False)

    except Exception as ex:
        if 't' in locals() and t.HasStarted() and not t.HasEnded():
            t.RollBack()
        forms.alert("Error importing Excel file:\n{}".format(str(ex)), title="OMTools | Error")

# 🚀 MAIN EXECUTION
# --------------------------------------------------------------------------
def main():
    components = [
        Label("Select action to perform:"),
        ComboBox("opcion_usuario", {
            "1. Export Sheet Data": "EXPORT",
            "2. Import Sheet Data": "IMPORT"
        }),
        Label("Bulk manage sheet metadata via Excel."),
        Button("Continue")
    ]

    form = FlexForm("OMTools | SheetSync", components)
    form.show()

    if not form.values:
        return

    seleccion = form.values.get("opcion_usuario")

    if seleccion == "EXPORT":
        ejecutar_exportacion()
    elif seleccion == "IMPORT":
        ejecutar_importacion()


if __name__ == "__main__":
    main()