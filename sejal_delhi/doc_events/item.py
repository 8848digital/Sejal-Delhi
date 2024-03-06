from __future__ import unicode_literals
import frappe
from frappe.model.naming import make_autoname
# Validate
def validate(doc, method):
    childtable = doc.get('custom_purchase_receipt_item_breakup_detail') or []
    other_total_weight = 0
    kun_total_weight = 0
    cs_total_weight = 0
    bb_total_weight = 0
    other_total_pcs = 0
    kun_total_pcs = 0
    cs_total_pcs = 0
    bb_total_pcs = 0

    for row in childtable:
        if row.material_group == 'Kundan':
            kun_total_weight += row.weight
            kun_total_pcs += row.pcs
        elif row.material_group == 'Colorstone':
            cs_total_weight += row.weight
            cs_total_pcs += row.pcs
        elif row.material_group == 'BlackBeads':
            bb_total_weight += row.weight
            bb_total_pcs += row.pcs
        else:
            other_total_weight += row.weight
            other_total_pcs += row.pcs

    # Set the total weight of materials
    doc.custom_other_wt = other_total_weight
    doc.custom_kun_wt = kun_total_weight
    doc.custom_cs_wt = cs_total_weight
    doc.custom_bb_wt = bb_total_weight
    doc.custom_other_pcs = other_total_pcs
    doc.custom_kun_pcs = kun_total_pcs
    doc.custom_cs_pcs = cs_total_pcs
    doc.custom_bb_pcs = bb_total_pcs



