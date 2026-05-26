# -*- coding: utf-8 -*-
__title__     = "Room Locator"
__author__    = "Oscar Mendoza"
__doc__ = """Version = 1.2
Date    = 26.05.2026
_____________________________________________________________________
Description:
Identifies rooms within a linked Architecture model and automatically 
assigns their Name and Number to the corresponding parameters of 
the furniture elements in the host model. Handles both point-based 
and curve-based (linear) furniture elements.
_____________________________________________________________________
How-to:
-> Ensure the Architecture (ARQ) link is loaded in the host model.
-> Verify that target parameters are created in the furniture elements.
-> Run the script from the pyRevit toolbar.
_____________________________________________________________________
Last update:
- [26.05.2026] - 1.2 Added LocationCurve support (Midpoint analysis)
________________________________________________________________________
Author: Oscar Mendoza"""

__helpurl__ = 'https://www.youtube.com/watch?v=dQw4w9WgXcQ'
__min_revit_ver__ = 2021
__max_revit_ver__ = 2026

# ⬇️ IMPORTS
# --------------------------------------------------------------------------
from Autodesk.Revit.DB import *
from Autodesk.Revit.UI.Selection import *
from pyrevit import forms, revit, script
from rpw.ui.forms import *

# 📦VARIABLES & DOCUMENT
# --------------------------------------------------------------------------
doc = revit.doc
uidoc = __revit__.ActiveUIDocument
selection = uidoc.Selection

# 1. BUSCAR Y SELECCIONAR VÍNCULO
# --------------------------------------------------------------------------
link_instances = FilteredElementCollector(doc).OfClass(RevitLinkInstance).ToElements()

if not link_instances:
    forms.alert("No se encontraron modelos vinculados en este proyecto.", title="Error de Vínculos")
    script.exit()

link_inst_dic = {x.Name: x for x in link_instances}
value_inst = SelectFromList('Selecciona el Vínculo de Arquitectura', link_inst_dic.keys())

link_doc = None
link_transform = None

if value_inst:
    selected_instance = link_inst_dic[value_inst]
    link_doc = selected_instance.GetLinkDocument()
    link_transform = selected_instance.GetTotalTransform()
else:
    script.exit()

# 2. VALIDACIÓN: ¿EL VÍNCULO TIENE ROOMS COLOCADOS?
# --------------------------------------------------------------------------
if link_doc:
    rooms_en_link = FilteredElementCollector(link_doc) \
        .OfCategory(BuiltInCategory.OST_Rooms) \
        .WhereElementIsNotElementType() \
        .ToElements()

    rooms_validos = [r for r in rooms_en_link if r.Area > 0]

    if not rooms_validos:
        forms.alert(
            "El modelo vinculado seleccionado NO contiene habitaciones (Rooms) válidas o colocadas.\n"
            "Verifica el archivo de arquitectura.",
            title="Validación de Rooms Fallida",
            warn_icon=True
        )
        script.exit()
else:
    forms.alert("El vínculo seleccionado no está cargado o no es accesible.", title="Error")
    script.exit()

# 3. SELECCIONAR MOBILIARIOS LOCALES
# --------------------------------------------------------------------------
mobiliarios = FilteredElementCollector(doc) \
    .OfCategory(BuiltInCategory.OST_Furniture) \
    .WhereElementIsNotElementType() \
    .ToElements()

if not mobiliarios:
    script.get_output().print_md("No se encontraron elementos de Mobiliario en el modelo local.")
    script.exit()

# 4. TRANSACCIÓN Y ASIGNACIÓN DE PARÁMETROS
# --------------------------------------------------------------------------
t = Transaction(doc, "Asignar Room desde Vínculo")
t.Start()

contador = 0

for mob in mobiliarios:
    location = mob.Location
    punto = None

    # CASO 1: El elemento se define por un Punto (Mobiliario estándar)
    if isinstance(location, LocationPoint):
        punto = location.Point

    # CASO 2: El elemento se define por una Línea/Curva (Mobiliario paramétrico/basado en líneas)
    elif isinstance(location, LocationCurve):
        curva = location.Curve
        # Evaluamos el parámetro 0.5 (obtiene el punto medio exacto de la curva, sea recta o curva)
        punto = curva.Evaluate(0.5, True)

    # Si logramos determinar un punto válido, hacemos el análisis geométrico
    if punto:
        punto_invertido = link_transform.Inverse.OfPoint(punto)

        # Buscar si hay un Room en esa posición dentro del modelo vinculado
        room = link_doc.GetRoomAtPoint(punto_invertido)

        if room:
            room_name = room.get_Parameter(BuiltInParameter.ROOM_NAME).AsString()
            room_number = room.get_Parameter(BuiltInParameter.ROOM_NUMBER).AsString()
            # Parametros
            p_nombre = mob.get_Parameter(BuiltInParameter.ALL_MODEL_INSTANCE_COMMENTS)
            p_numero = mob.get_Parameter(BuiltInParameter.ALL_MODEL_MARK)

            if p_nombre and not p_nombre.IsReadOnly:
                p_nombre.Set(room_name)
            if p_numero and not p_numero.IsReadOnly:
                p_numero.Set(room_number)

            contador += 1

t.Commit()

# 5. RESULTADOS
# --------------------------------------------------------------------------
output = script.get_output()
output.print_md("### **Proceso Finalizado con Éxito**")
output.print_md("Se analizaron los Rooms de: **{}**".format(value_inst))
output.print_md("Se actualizaron **{}** elementos de mobiliario.".format(contador))