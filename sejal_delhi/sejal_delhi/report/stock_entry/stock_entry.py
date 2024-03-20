# Copyright (c) 2023, 8848 and contributors
# For license information, please see license.txt
import frappe
import json
import pdfkit
from io import BytesIO
from datetime import datetime
from frappe import _

import frappe

def execute(filters=None):
    conditions = get_conditions(filters)
    columns = [
        {
            "label": "Warehouse",
            "fieldname": "warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 250
        },
        {
            "label": "Item Code",
            "fieldname": "item_code",
            "fieldtype": "Link",
            "options": "Item",
            "width": 250
        }
    ]
    data = frappe.db.sql(f"""
        SELECT sle.warehouse, sle.item_code
        FROM `tabStock Ledger Entry` AS sle
        WHERE docstatus = 1 AND qty_after_transaction = 1
        {conditions}
    """, as_dict=True)
    return columns, data

def get_conditions(filters):
    conditions = ""
    if filters and filters.get('item_code') and filters.get('item_code') != "":
        conditions += f'AND sle.item_code = "{filters.get("item_code")}"'
    if filters and filters.get('warehouse') and filters.get('warehouse') != "":
        conditions += f'AND sle.warehouse = "{filters.get("warehouse")}"'
    return conditions


