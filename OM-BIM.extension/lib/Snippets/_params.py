# -*- coding: utf-8 -*-
# ⬇️ IMPORTS
#--------------------------------------------------------------------------
from Autodesk.Revit.DB import *
import System
from Autodesk.Revit.UI.Selection import *


#📦VARIABLES
#--------------------------------------------------------------------------
uidoc = __revit__.ActiveUIDocument   #type: Document
doc = __revit__.ActiveUIDocument.Document
app = __revit__.Application
selection = uidoc.Selection

categories_spanish = ["Conexiones estructurales", "Refuerzo de área estructural", "Armadura estructural",
                      "Tramos de bandeja de cables", "Tramos de tubo", "Tubos", "Bandejas de cables",
                      "Uniones de tubo", "Uniones de bandeja de cables", "Aislamientos de conducto",
                      "Aislamientos de tubería", "Sistema de interruptores", "Rociadores", "Dispositivos de iluminación",
                      "Dispositivos de alarma de incendios", "Dispositivos de datos", "Dispositivos de comunicación",
                      "Dispositivos de seguridad", "Timbres de enfermería", "Dispositivos telefónicos",
                      "Accesorios de tuberías", "Tuberías flexibles", "Uniones de tubería", "Tuberías",
                      "Conductos flexibles", "Accesorios de conductos", "Terminales de aire", "Uniones de conducto",
                      "Conductos", "Masa", "Vegetación", "Equipos especializados", "Topografía", "Pilares estructurales",
                      "Armazón estructural", "Cimentación estructural", "Emplazamiento", "Aparatos sanitarios",
                      "Equipos mecánicos", "Luminarias", "Sistemas de mobiliario", "Aparatos eléctricos",
                      "Equipos eléctricos", "Equipo de zona", "Muebles de obra", "Sistemas de muro cortina",
                      "Rampas", "Montantes de muro cortina", "Paneles de muro cortina", "Modelos genéricos",
                      "Barandillas", "Escaleras", "Pilares", "Mobiliario", "Suelos", "Puertas","Información de proyecto",
                      "Ventanas", "Muros"]

categories_en =["Structural Connections", "Structural Area Reinforcement", "Structural Rebar", "Cable Tray Runs",
                "Conduit Runs", "Pipes", "Cable Trays", "Conduit Fittings", "Cable Tray Fittings", "Duct Insulations",
                "Pipe Insulations", "Switch Systems", "Sprinklers", "Lighting Devices", "Fire Alarm Devices",
                "Data Devices", "Communication Devices", "Security Devices", "Nurse Call Devices", "Telephone Devices",
                "Pipe Accessories", "Flex Pipes", "Pipe Fittings", "Piping", "Flex Ducts", "Duct Accessories",
                "Air Terminals", "Duct Fittings", "Ducts", "Mass", "Planting", "Specialty Equipment", "Topography",
                "Structural Columns", "Structural Framing", "Structural Foundations", "Site", "Plumbing Fixtures",
                "Mechanical Equipment", "Lighting Fixtures", "Furniture Systems", "Electrical Fixtures",
                "Electrical Equipment", "Zone Equipment", "Casework", "Curtain Wall Systems", "Ramps",
                "Curtain Wall Mullions", "Curtain Wall Panels", "Generic Models", "Railings", "Stairs", "Columns",
                "Furniture", "Ceilings", "Roofs", "Floors", "Doors", "Windows", "Walls"]

parameter_groups = {
    "Texto": GroupTypeId.Text,
    "Datos": GroupTypeId.Data,
    "Datos de identidad": GroupTypeId.IdentityData,
    "Electrico": GroupTypeId.Electrical,
    "General": GroupTypeId.General,
    "Visualización": GroupTypeId.Visibility,
    "Parámetros IFC": GroupTypeId.Ifc
}

def get_doc_categories( include_subcats=False):
    """
    Retrieves all categories from the given Revit document, optionally including subcategories.
    """
    all_cats = []
    cats = doc.Settings.Categories
    all_cats.extend(cats)
    if include_subcats:
        for cat in cats:
            all_cats.extend([x for x in cat.SubCategories])
    return all_cats

def get_category():
    language = str(app.Language)
    if language == "Spanish":
        category_dic={}
        all_cats = get_doc_categories(doc)
        for cat in all_cats:
            for cats in categories_spanish:
                if cat.Name == cats:
                    category_dic[cats] = cat
        return  category_dic

def get_parameter_group():
    return parameter_groups