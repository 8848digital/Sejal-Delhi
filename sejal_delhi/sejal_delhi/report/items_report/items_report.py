# Copyright (c) 2024, Deepak Kumar and contributors
# For license information, please see license.txt

# import frappe


def execute(filters=None):
	columns, data = [], []
	return columns, data


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
			"label": "Item Code",
			"fieldname": "name",
			"fieldtype": "Link",
			"options": "Item",
			"width": 250,
		},
		{
			"label": "Custom Gross Wt",
			"fieldname": "custom_gross_wt",
			"fieldtype": "Data",
			"width": 250,
		},
		{
			"label": "Custom Net Wt",
			"fieldname": "custom_net_wt",
			"fieldtype": "Data",
			"width": 250,
		},
		{
			"label": "Karigar",
			"fieldname": "custom_karigar",
			"fieldtype": "Link",
			"options": "karigar",
			"width": 250,
		},
	]
	data = frappe.db.sql(
		f"""
        SELECT
		item.name,
		item.custom_gross_wt,
        item.custom_net_wt,
        item.custom_karigar
        FROM `tabItem` as item

        {conditions}
    """,
		as_dict=True,
	)
	return columns, data


def get_conditions(filters):
	conditions = ""
	if filters and filters.get("name") and filters.get("name") != "":
		conditions += f' WHERE item.name = "{filters.get("name")}"'
	if filters and filters.get("custom_karigar") and filters.get("custom_karigar") != "":
		if conditions:
			conditions += f' AND item.custom_karigar = "{filters.get("custom_karigar")}"'
		else:
			conditions += f' WHERE item.custom_karigar = "{filters.get("custom_karigar")}"'
	return conditions
