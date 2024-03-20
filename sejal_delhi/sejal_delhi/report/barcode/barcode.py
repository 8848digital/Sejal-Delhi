import frappe
from frappe.utils import getdate


def execute(filters=None):
	columns, data = [], []
	# Define your columns
	columns = [
		{"label": "Index", "fieldname": "idx", "fieldtype": "Int"},
		{"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date"},
		{"label": "Custom Karigar", "fieldname": "custom_karigar", "fieldtype": "Data"},
		{"label": "Item Code", "fieldname": "item_code", "fieldtype": "Data", "width": 150},
		{"label": "Source", "fieldname": "source", "fieldtype": "Data", "width": 150},
	]
	purchase_receipt_conditions = ""
	delivery_note_conditions = ""
	purchase_receipt_filters_list = []
	delivery_note_filters_list = []
	posting_date = filters.get("posting_date")
	custom_karigar = filters.get("custom_karigar")
	sr_from = filters.get("sr_from")
	sr_to = filters.get("sr_to")
	item_code = filters.get("item_code")
	name = filters.get("name")
	if posting_date:
		posting_date_01 = frappe.utils.getdate(posting_date).strftime("%Y-%m-%d")
		purchase_receipt_filters_list.append(f'posting_date = "{posting_date_01}"')
		delivery_note_filters_list.append(f'posting_date = "{posting_date_01}"')
	if custom_karigar:
		purchase_receipt_filters_list.append(f'custom_karigar = "{custom_karigar}"')
		delivery_note_filters_list.append(f'custom_client_name = "{custom_karigar}"')
	if sr_from and sr_to:
		srfrom = int(sr_from)
		srto = int(sr_to)
		purchase_receipt_filters_list.append(
			f"CAST(SUBSTRING(item_code, 5) AS SIGNED) BETWEEN {srfrom} AND {srto}"
		)
		delivery_note_filters_list.append(
			f"CAST(SUBSTRING(item_code, 5) AS SIGNED) BETWEEN {srfrom} AND {srto}"
		)
	if name:
		purchase_receipt_filters_list.append(f'item_code LIKE "{name}%"')
		delivery_note_filters_list.append(f'item_code LIKE "{name}%"')
	if purchase_receipt_filters_list:
		purchase_receipt_conditions = "AND " + " AND ".join(purchase_receipt_filters_list)
	if delivery_note_filters_list:
		delivery_note_conditions = "AND " + " AND ".join(delivery_note_filters_list)
	if item_code == "A":
		query_a = f"""
        SELECT
            'Purchase Receipt' AS source,
            pri.item_code AS item_code,
            pr.posting_date AS posting_date,
            pr.custom_karigar AS custom_karigar
        FROM
            `tabPurchase Receipt` AS pr
        LEFT JOIN
            `tabPurchase Receipt Item` AS pri ON pri.parent = pr.name
        WHERE 1=1 {purchase_receipt_conditions}
        """
		query_b = f"""
        # UNION ALL
        # SELECT
        #     'Delivery Note (Sales Return)' AS source,
        #     dni.item_code AS item_code,
        #     dn.posting_date AS posting_date,
        #     dn.custom_client_name AS custom_karigar
        # FROM
        #     `tabDelivery Note` AS dn
        # LEFT JOIN
        #     `tabDelivery Note Item` AS dni ON dni.parent = dn.name
        # WHERE
        #     dn.is_return = 1 {delivery_note_conditions}
        """
	else:
		query_b = ""
	if item_code == "G":
		query_a = f"""
        SELECT
            'Delivery Note (Sales)' AS source,
            dni.item_code AS item_code,
            dn.posting_date AS posting_date,
            dn.custom_client_name AS custom_karigar
        FROM
            `tabDelivery Note` AS dn
        LEFT JOIN
            `tabDelivery Note Item` AS dni ON dni.parent = dn.name
        WHERE
            dn.is_return = 0 {delivery_note_conditions}
        """
	if item_code == None:
		query_a = f"""
            SELECT
                'Purchase Receipt' AS source,
                pri.item_code AS item_code,
                pr.posting_date AS posting_date,
                pr.custom_karigar AS custom_karigar
            FROM
                `tabPurchase Receipt` AS pr
            LEFT JOIN
                `tabPurchase Receipt Item` AS pri ON pri.parent = pr.name
            WHERE 1=1 {purchase_receipt_conditions}
        """
	print(query_a + query_b)
	data = frappe.db.sql(query_a + query_b, as_dict=True)
	return columns, data