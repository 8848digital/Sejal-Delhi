import frappe
from frappe.model.naming import make_autoname

def autoname(doc, method):
    if doc.is_return:
        # SR series
        series = 'SR-.DD.-.MM.-.YYYY.-'
    else:
        # SA series
        series = 'SA-.DD.-.MM.-.YYYY.-'
    doc.naming_series = series
    doc.name = make_autoname(doc.naming_series + ".###", "", doc)