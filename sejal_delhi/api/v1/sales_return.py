import frappe
import json


def error_response(err_msg):
	return {"status": "error", "message": err_msg}


def success_response(data, name):
	return {"status": "success", "data": data, "name": name}


@frappe.whitelist(allow_guest=True)
def create_delivery_note_sales_return(kwargs):
	try:
		item_code_list = frappe.db.sql(
			f"""SELECT dni.item_code
                    FROM `tabDelivery Note` As dn
                    LEFT JOIN  `tabDelivery Note Item` AS dni ON dni.parent = dn.name
                    WHERE dn.is_return = 1
                """
		)

		flattened_list = [item for sublist in item_code_list for item in sublist]
		items = kwargs.get("items", [])
		purchase_receipt_status = frappe.db.sql(
			f"""SELECT sle.item_code
                                                FROM `tabStock Ledger Entry` AS sle
                                                WHERE sle.item_code = '{items[0].get("item_code")}' AND sle.voucher_type = 'Delivery Note'
                                                """
		)

		if items[0].get("item_code") not in flattened_list:
			if len(purchase_receipt_status) % 2 != 0:
				if kwargs:
					request_data = kwargs  # kwargs is already a dictionary
					items = request_data.get("items", [])
					doc = frappe.new_doc("Delivery Note")
					del_note_item_id = frappe.db.get_value(
						"Item", items[0].get("item_code"), "custom_delivery_note"
					)

					doc.update(
						{
							"name": request_data.get("name"),
							"customer": "shyam",
							"custom_client_name": request_data.get("custom_client_name"),
							"custom_kun_category": request_data.get("custom_kun_category"),
							"custom_cs_category": request_data.get("custom_cs_category"),
							"custom_bb_category": request_data.get("custom_bb_category"),
							"custom_ot_category": request_data.get("custom_ot_category"),
							"is_return": request_data.get("is_return"),
							"return_against": del_note_item_id,
						}
					)

					custom_client_name = request_data.get("custom_client_name")
					custom_client_group = request_data.get("custom_client_group")
					if custom_client_name and not frappe.db.exists("Client", custom_client_name):
						new_client = frappe.get_doc(
							{
								"doctype": "Client",
								"client_name": custom_client_name,
								"client_group": custom_client_group,
							}
						)
						new_client.insert(ignore_permissions=True)

					items = request_data.get("items", [])  # Safely access the 'items' key
					warehouse = frappe.db.get_value(
						"Warehouse",
						{"custom_store_location": request_data.get("store_location")},
						["name"],
					)
					for challan in items:
						doc.append(
							"items",
							{
								"doctype": "Delivery Note Item",
								"item_code": challan.get("item_code"),
								"item_name": challan.get("item_name"),
								"qty": -1.00,
								"uom": "Nos",
								"custom_kun_wt": challan.get("custom_kun_wt"),
								"custom_gross_wt": challan.get("custom_gross_wt"),
								"custom_cs_wt": challan.get("custom_cs_wt"),
								"custom_bb_wt": challan.get("custom_bb_wt"),
								"custom_other_wt": challan.get("custom_other_wt"),
								"custom_net_wt": challan.get("custom_net_wt"),
								"custom_cs": challan.get("custom_cs"),
								"custom_cs_amt": challan.get("custom_cs_amt"),
								"custom_kun_pc": challan.get("custom_kun_pc"),
								"custom_kun": challan.get("custom_kun"),
								"custom_kun_amt": challan.get("custom_kun_amt"),
								"custom_ot_": challan.get("custom_ot_"),
								"custom_ot_amt": challan.get("custom_ot_amt"),
								"custom_other": challan.get("custom_other"),
								"custom_amount": challan.get("custom_amount"),
								"warehouse": warehouse,
							},
						)

					doc.insert(ignore_permissions=True)

					# Assuming 'tabItem' is the correct table name
					frappe.db.set_value(
						"Item",
						challan.get("item_code"),
						"custom_return_delivery_note",
						doc.name,
					)

					return success_response(
						data="Successfully created with name " + doc.name, name=doc.name
					)
			else:
				return error_response(f"""Delivery Note of Item Code Is not Submitted""")
		else:
			return error_response("Item code already exist in Delivery Note Item")

	except Exception as e:
		frappe.logger("delivery_create").exception(e)
		return error_response(str(e))


@frappe.whitelist(allow_guest=True)
def get_specific_delivery_note_sales_return(kwargs):
	name = kwargs.get("name")

	our_specific = []
	list1 = frappe.get_all(
		"Delivery Note",
		filters={"name": name},
		fields=[
			"name",
			"posting_date",
			"custom_client_name",
			"custom_kun_category",
			"custom_bb_category",
			"custom_ot_category",
			"is_return",
			"docstatus",
		],
	)

	for l in list1:

		table = {
			"name": l.name,
			"posting_date": l.posting_date,
			"custom_client_name": l.custom_client_name,
			"kun_category": l.custom_kun_category,
			"cs_category": l.custom_cs_category,
			"bb_category": l.custom_bb_category,
			"oth_category": l.custom_ot_category,
			"is_return": l.is_return,
			"docstatus": l.docstatus,
			"items": [],
		}

		child_table_list = frappe.get_all(
			"Delivery Note Item",
			filters={"parent": l.name},
			fields=[
				"idx",
				"item_code",
				"custom_kun_wt",
				"custom_cs_wt",
				"custom_gross_wt",
				"custom_bb_wt",
				"custom_other_wt",
				"custom_net_wt",
				"custom_cs",
				"custom_cs_amt",
				"custom_kun_pc",
				"custom_kun",
				"custom_kun_amt",
				"custom_ot_",
				"custom_ot_amt",
				"custom_other",
				"custom_amount",
				"warehouse",
			],
			order_by="idx ASC",
		)

		for row in child_table_list:
			table["items"].append(
				{
					"idx": row.idx,
					"item_code": row.item_code,
					"custom_kun_wt": row.custom_kun_wt,
					"custom_cs_wt": row.custom_cs_wt,
					"custom_gross_wt": row.custom_gross_wt,
					"custom_bb_wt": row.custom_bb_wt,
					"custom_other_wt": row.custom_other_wt,
					"custom_net_wt": row.custom_net_wt,
					"custom_cs": row.custom_cs,
					"custom_cs_amt": row.custom_cs_amt,
					"custom_kun_pc": row.custom_kun_pc,
					"custom_kun": row.custom_kun,
					"custom_kun_amt": row.custom_kun_amt,
					"custom_ot_": row.custom_ot_,
					"custom_ot_amt": row.custom_ot_amt,
					"custom_other": row.custom_other,
					"custom_amount": row.custom_amount,
					"warehouse": row.warehouse,
				}
			)
		our_specific.append(table)
	# response_data = {
	#     "data": our_specific
	# }
	return build_response("success", data=table)


def build_response(status, data=None, message=None):
	response = {"status": status}
	if data is not None:
		response["data"] = data
	if message is not None:
		response["message"] = message
	return response


@frappe.whitelist(allow_guest=True)
def put_delivery_note_sales_return(data):
	try:
		if frappe.request.method == "PUT":
			data = json.loads(frappe.request.data)
			delivery_note_name = data.get("name")
			if frappe.db.exists("Delivery Note", delivery_note_name):
				custom_client_name = data.get("custom_client_name")
				if custom_client_name and not frappe.db.exists("Client", custom_client_name):
					new_client = frappe.get_doc(
						{
							"doctype": "Client",
							"client_name": custom_client_name,
							"client_group": "ABCDasa6sdf",  # Adjust this according to your requirements
						}
					)
					new_client.insert(ignore_permissions=True)

				delivery_note = frappe.get_doc("Delivery Note", delivery_note_name)
				delivery_note.custom_client_name = data.get("custom_client_name")
				delivery_note.is_return = data.get("is_return")
				delivery_note.custom_kun_category = data.get("custom_kun_category")
				delivery_note.custom_cs_category = data.get("custom_cs_category")
				delivery_note.custom_bb_category = data.get("custom_bb_category")
				delivery_note.custom_ot_category = data.get("custom_ot_category")

				items = data.get("items", [])  # Safely access the 'items' key
				delivery_note.items = []

				warehouse = frappe.db.get_value(
					"Warehouse",
					{"custom_store_location": data.get("store_location")},
					["name"],
				)

				for challan in items:

					new_item = frappe.get_doc(
						{
							"idx": challan.get("idx"),
							"doctype": "Delivery Note Item",
							"parent": delivery_note.name,
							"item_code": challan.get("item_code"),
							"item_name": "nfsam-24",
							"description": "description",
							"qty": 1.00,
							"uom": "Nos",
							"conversion_factor": 0.00,
							"parenttype": "Delivery Note",
							"custom_kun_wt": challan.get("custom_kun_wt"),
							"custom_gross_wt": challan.get("custom_gross_wt"),
							"custom_cs_wt": challan.get("custom_cs_wt"),
							"custom_bb_wt": challan.get("custom_bb_wt"),
							"custom_other_wt": challan.get("custom_other_wt"),
							"custom_net_wt": challan.get("custom_net_wt"),
							"custom_cs": challan.get("custom_cs"),
							"custom_cs_amt": challan.get("custom_cs_amt"),
							"custom_kun_pc": challan.get("custom_kun_pc"),
							"custom_kun": challan.get("custom_kun"),
							"custom_kun_amt": challan.get("custom_kun_amt"),
							"custom_ot_": challan.get("custom_ot_"),
							"custom_ot_amt": challan.get("custom_ot_amt"),
							"custom_other": challan.get("custom_other"),
							"custom_amount": challan.get("custom_amount"),
							"warehouse": warehouse,
							# need warehouse as well
							# Assign other fields here as needed
						}
					)
					frappe.db.set_value(
						"Item",
						challan.get("item_code"),
						"custom_return_delivery_note",
						delivery_note.name,
					)

					new_item.insert(ignore_permissions=True)
					delivery_note.append("items", new_item)

				delivery_note.save(ignore_permissions=True)
				frappe.db.commit()

				return success_response(
					data="Successfully created with name " + delivery_note.name,
					name=delivery_note.name,
				)
			else:
				return error_response("No such record exists")

	except Exception as e:
		frappe.db.rollback()
		frappe.logger("Put Delivery Note").exception(e)
		frappe.log_error(title=_("API Error"), message=e)
		return error_response(str(e))


from frappe import _


@frappe.whitelist(allow_guest=True)
def get_delivery_note_specific_return_item(kwargs):
	name = kwargs.get("name")
	conditions = get_conditions(name)

	try:
		data = frappe.db.sql(
			f"""
            SELECT DISTINCT

                item.item_code,
                dn.custom_client_name,
                delivery_note_item.idx,
                delivery_note_item.custom_kun_wt,
                delivery_note_item.custom_gross_wt,
                delivery_note_item.custom_cs_wt,
                delivery_note_item.custom_bb_wt,
                delivery_note_item.custom_other_wt,
                delivery_note_item.custom_net_wt,
                delivery_note_item.custom_cs,
                delivery_note_item.custom_cs_amt,
                delivery_note_item.custom_kun_pc,
                delivery_note_item.custom_kun,
                delivery_note_item.custom_kun_amt,
                delivery_note_item.custom_ot_,
                delivery_note_item.custom_ot_amt,
                delivery_note_item.custom_other,
                delivery_note_item.custom_amount,
                delivery_note_item.warehouse
            FROM `tabItem` AS item
            LEFT JOIN `tabDelivery Note` AS dn ON item.custom_delivery_note = dn.name
            RIGHT JOIN `tabDelivery Note Item` AS delivery_note_item ON item.name = delivery_note_item.item_code
            WHERE 1=1 {conditions}
        """,
			as_dict=True,
		)

		if data:
			response_data = [
				{
					"idx": record.get("idx"),
					"item_code": record.get("item_code"),
					"custom_kun_wt": record.get("custom_kun_wt"),
					"custom_gross_wt": record.get("custom_gross_wt"),
					"custom_cs_wt": record.get("custom_cs_wt"),
					"custom_bb_wt": record.get("custom_bb_wt"),
					"custom_other_wt": record.get("custom_other_wt"),
					"custom_net_wt": record.get("custom_net_wt"),
					"custom_cs": record.get("custom_cs"),
					"custom_cs_amt": record.get("custom_cs_amt"),
					"custom_kun_pc": record.get("custom_kun_pc"),
					"custom_kun": record.get("custom_kun"),
					"custom_kun_amt": record.get("custom_kun_amt"),
					"custom_ot_": record.get("custom_ot_"),
					"custom_ot_amt": record.get("custom_ot_amt"),
					"custom_other": record.get("custom_other"),
					"custom_amount": record.get("custom_amount"),
					"warehouse": record.get("warehouse"),
				}
				for record in data
			]

			client_name = (
				data[0].get("custom_client_name") if data[0].get("custom_client_name") else None
			)

			response = {
				"status": "success",
				"data": [{"custom_client_name": client_name, "items": response_data}],
				"exec_time": "0.0004 seconds",
			}

			return response
		else:
			return {"status": "success", "data": [], "exec_time": "0.0004 seconds"}
	except Exception as e:
		frappe.log_error(title=_("API Error"), message=str(e))
		return {"status": "error", "message": "An error occurred while fetching data."}


def get_conditions(name=None):
	conditions = ""
	if name:
		conditions += f' AND item.name = "{name}"'

	return conditions


import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_listening_delivery_note_sales_return(kwargs):
	try:
		data = frappe.db.sql(
			"""
            SELECT
                dn.is_return,
                dn.custom_number,
                dn.name,
                dn.posting_date,
                dn.custom_client_name,
                dn.docstatus
            FROM
                `tabDelivery Note` AS dn
            WHERE
                (dn.docstatus = 0 or dn.docstatus = 1 or dn.docstatus = 2)
                AND dn.name NOT IN (SELECT amended_from FROM `tabDelivery Note` WHERE amended_from IS NOT NULL)
            ORDER BY
                modified desc
        """,
			as_dict=True,
		)
		return build_response("success", data=data)
	except Exception as e:
		frappe.log_error(title=_("API Error"), message=str(e))
		return build_response("error", message=_("An error occurred while fetching data."))


def build_response(status, data=None, message=None):
	response = {"status": status}

	if data is not None:
		response["data"] = data

	if message is not None:
		response["message"] = message

	return response


@frappe.whitelist(allow_guest=True)
def delete_delivery_note_sales_return(kwargs):
	name = kwargs.get("name")
	response_data = {}

	# Clear custom fields in associated items
	for field in [
		"custom_purchase_receipt",
		"custom_delivery_note",
		"custom_return_delivery_note",
	]:
		cus_dil = frappe.db.get_all("Item", {field: name}, ["name"])
		for item in cus_dil:
			item_doc = frappe.get_doc("Item", item.get("name"))
			if item_doc.docstatus != 2:
				setattr(item_doc, field, "")
				item_doc.save(ignore_permissions=True)

	# Clear voucher_no in associated Repost Item Valuation
	cus_dil = frappe.db.get_all(
		"Repost Item Valuation",
		{
			"voucher_no": name,
		},
		["name"],
	)
	for item in cus_dil:
		item_doc = frappe.get_doc("Repost Item Valuation", item.get("name"))
		if item_doc.docstatus != 2:
			item_doc.voucher_no = ""
			item_doc.cancel()

	if frappe.db.exists("Delivery Note", name):
		try:
			frappe.delete_doc("Delivery Note", name)
			response_data = {
				"message": f"Delivery Note {name} deleted successfully.",
				"status": "success",
			}
		except Exception as e:
			response_data = {"message": str(e), "status": "error"}
	else:
		response_data = {
			"message": f"Delivery Note {name} not found.",
			"status": "error",
		}

	return response_data
