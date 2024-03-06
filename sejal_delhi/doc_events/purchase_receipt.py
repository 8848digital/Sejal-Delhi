import frappe
from frappe.model.naming import make_autoname


def autoname(doc, method):
    doc.naming_series = 'RR-.DD.-.MM.-.YYYY.-'
    doc.name = make_autoname(doc.naming_series + ".###", "", doc)
    
def number_set(doc, method):
    if doc.amended_from:
        # we have two -
        last = doc.name.split("-")[-1]
        second_last = doc.name.split("-")[-2]
        doc.custom_number = second_last + "-" + last
    else:
        doc.custom_number = doc.name.split("-")[-1]
