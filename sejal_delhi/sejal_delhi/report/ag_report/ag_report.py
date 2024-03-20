# Copyright (c) 2024, shyam and contributors
# For license information, please see license.txt

# import frappe


def execute(filters=None):
	columns, data = [], []
	return columns, data
# Copyright (c) 2024, Deepak Kumar and contributors
# For license information, please see license.txt

import frappe
from frappe import _

def execute(filters=None):
    columns = [
        {
            "label": _("Item Code"),
            "fieldname": "item_code",
            "fieldtype": "Data",
            "width": 150
        },
        {
            "label": _("Source"),
            "fieldname": "source",
            "fieldtype": "Data",
            "width": 150
        }
    ]

    item_code = filters.get("item_code")

    if item_code == "A":
        sql_query = """
            SELECT 
                'Purchase Receipt' AS source,
                pri.item_code
            FROM 
                `tabPurchase Receipt` AS pr
            LEFT JOIN 
                `tabPurchase Receipt Item` AS pri ON pri.parent = pr.name
            
            UNION ALL
            
            SELECT 
                'Delivery Note (Sales Return)' AS source,
                dni.item_code
            FROM 
                `tabDelivery Note` AS dn
            LEFT JOIN 
                `tabDelivery Note Item` AS dni ON dni.parent = dn.name
            WHERE 
                dn.is_return = 1
        """
    elif item_code == "G":
        sql_query = """
            SELECT 
                'Delivery Note (Sales)' AS source,
                dni.item_code
            FROM 
                `tabDelivery Note` AS dn
            LEFT JOIN 
                `tabDelivery Note Item` AS dni ON dni.parent = dn.name
            WHERE 
                dn.is_return = 0
        """
    else:
        # If item_code is neither 'A' nor 'G', return an empty result
        columns = []
        data = []
        return columns, data

    data = frappe.db.sql(sql_query, as_dict=True)

    return columns, data