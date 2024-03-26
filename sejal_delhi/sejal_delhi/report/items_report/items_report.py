import frappe
from frappe import _

def execute(filters=None):
    limit_start = filters.get("limit_start", 0)
    limit_page_length = filters.get("limit_page_length", 10)
    if limit_page_length == "ALL":
        limit_clause = ""
    else:
        limit_clause = f"LIMIT {limit_start}, {limit_page_length}"
    conditions = get_conditions(filters)
    columns = [
        {
            "label": "Item Code",
            "fieldname": "name",
            "fieldtype": "Link",
            "options": "Item",
            "width": 200,
        },
        {
            "label": "Custom Gross Wt",
            "fieldname": "custom_gross_wt",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": "Custom Net Wt",
            "fieldname": "custom_net_wt",
            "fieldtype": "Data",
            "width": 200,
        },
        {
            "label": "Karigar",
            "fieldname": "custom_karigar",
            "fieldtype": "Link",
            "options": "karigar",
            "width": 200,
        },
        {
            "label": "Location",
            "fieldname": "custom_warehouse",
            "fieldtype": "Link",
            "options": "Warehouse",
            "width": 200,
        },
    ]

    data = frappe.db.sql(
        f"""
        SELECT
            item.name,
            item.custom_gross_wt,
            item.custom_net_wt,
            item.custom_karigar,
            item.custom_warehouse as custom_warehouse
        FROM `tabItem` as item
        {conditions}
        {limit_clause}
        """,
        as_dict=True,
    )
    return columns, data

def get_conditions(filters):
    conditions = []
    if filters and filters.get("name") and filters.get("name") != "":
        conditions.append(f'item.name = "{filters.get("name")}"')
    if filters and filters.get("custom_karigar") and filters.get("custom_karigar") != "":
        conditions.append(f'item.custom_karigar = "{filters.get("custom_karigar")}"')
    if filters and filters.get("custom_warehouse") and filters.get("custom_warehouse") != "":
        conditions.append(f'item.custom_warehouse = "{filters.get("custom_warehouse")}"')
           

    if conditions:
        return "WHERE " + " AND ".join(conditions)
    else:
        return ""
