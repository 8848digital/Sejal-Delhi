import frappe
import json


def error_response(err_msg):
	return {"status": "error", "message": err_msg}


def success_response(data, name):
	return {"status": "success", "data": data, "name": name}


@frappe.whitelist(allow_guest=True)
def create_delivery_note(kwargs):
	X={}
	try:
		item_code_list = frappe.db.sql(
			f"""SELECT dni.item_code
                      FROM `tabDelivery Note` As dn
                      LEFT JOIN  `tabDelivery Note Item` AS dni ON dni.parent = dn.name

                    """
		)

		flattened_list = [item for sublist in item_code_list for item in sublist]

		items = kwargs.get("items", [])

		purchase_receipt_status = frappe.db.sql(
			f"""SELECT sle.item_code
                FROM `tabStock Ledger Entry` AS sle
                WHERE sle.item_code = '{items[0].get("item_code")}' AND sle.voucher_type = 'Purchase Receipt'
                """
		)

		if items[0].get("item_code") not in flattened_list or (
			flattened_list.count(items[0].get("item_code")) % 2 == 0
			and flattened_list.count(items[0].get("item_code")) > 0
		):
			if len(purchase_receipt_status) % 2 != 0:
				if kwargs:
					request_data = kwargs  # kwargs is already a dictionary

					doc = frappe.new_doc("Delivery Note")
					doc.update(
						{
							"name": request_data.get("name"),
							"customer": "shyam",
							"custom_client_name": request_data.get("custom_client_name"),
							"custom_kun_category": request_data.get("custom_kun_category"),
							"custom_cs_category": request_data.get("custom_cs_category"),
							"custom_bb_category": request_data.get("custom_bb_category"),
							"custom_ot_category": request_data.get("custom_ot_category"),
							"custom_is_barcode": request_data.get("custom_is_barcode"),
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
					# get warehouse based on store location
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
								"qty": 1.00,
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
					# update delivery note in Item
					for item in doc.items:
						frappe.db.set_value("Item", item.item_code, "custom_delivery_note", doc.name)
					frappe.db.commit()
					return success_response(
						data="Successfully created with name " + doc.name, name=doc.name
					)
				
			else:
				return error_response(f"""Ready Receipt of Item Code Is not Submitted""")
		else:
			return error_response("Item code already exist in Delivery Note Item")
	except Exception as e:
		frappe.logger("delivery_create").exception(e)
		return error_response(str(e))


@frappe.whitelist(allow_guest=True)
def get_delivery_note(kwargs):
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
		],
	)
	for l in list1:
		table = {
			"name": l.name,
			"transaction date": l.posting_date,
			"Client": l.custom_client_name,
			"Kun Category": l.custom_kun_category,
			"CS Category": l.custom_cs_category,
			"BB Category": l.custom_bb_category,
			"Oth Category": l.custom_ot_category,
			"Items": [],
		}
		child_table_list = frappe.get_all(
			"Delivery Note Item",
			filters={"parent": l.name},
			fields=[
				"item_code",
				"custom_kun_wt",
				"custom_cs_wt",
				"custom_gross_wt",
				"custom_cs_wt",
				"custom_bb_wt",
				"custom_other_wt",
				"custom_net_wt",
				"custom_cs",
				"custom_cs_amt",
				"custom_kun_pc",
				"custom_kun",
				"custom_kun_amt",
				"custom_ot_amt",
				"custom_other",
				"custom_amount",
				"warehouse",
			],
		)
		for row in child_table_list:

			# custom_kun_wt = frappe.db.get_value("Item",row.item_code,"custom_kun_wt")

			table["Items"].append(
				{
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
					# "custom_pr_kun_wt":custom_kun_wt
				}
			)
		our_specific.append(table)
	response_data = {"data": our_specific}
	return build_response("success", data=response_data)


def build_response(status, data=None, message=None):
	response = {"status": status}
	if data is not None:
		response["data"] = data
	if message is not None:
		response["message"] = message
	return response


import frappe
from frappe import _
from frappe.utils.response import build_response
import json
from datetime import date


@frappe.whitelist(allow_guest=True)
def build_response(status, data=None, message=None):
	response = {"status": status}
	if data is not None:
		response["data"] = data
	if message is not None:
		response["message"] = message
	return response


@frappe.whitelist(allow_guest=True)
def put_delivery_note(kwargs):
	try:
		if frappe.request.method == "PUT":
			data = json.loads(frappe.request.data)
			# return data
			delivery_note_name = data.get("name")
			items = data.get("items", [])

			purchase_receipt_status = frappe.db.sql(
				f"""SELECT sle.item_code
                                                FROM `tabStock Ledger Entry` AS sle
                                                WHERE sle.item_code = '{items[0].get("item_code")}' AND sle.voucher_type = 'Purchase Receipt'
                                                """
			)

			if frappe.db.exists("Delivery Note", delivery_note_name):
				if len(purchase_receipt_status) % 2 != 0:
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
					delivery_note.custom_kun_category = data.get("custom_kun_category")
					delivery_note.custom_cs_category = data.get("custom_cs_category")
					delivery_note.custom_bb_category = data.get("custom_bb_category")
					delivery_note.custom_ot_category = data.get("custom_ot_category")
					delivery_note.custom_is_barcode = data.get("custom_is_barcode")

					warehouse = frappe.db.get_value(
						"Warehouse",
						{"custom_store_location": data.get("store_location")},
						["name"],
					)
					delivery_note.items = []
					for challan in items:

						new_item = frappe.get_doc(
							{
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
							}
						)
						frappe.db.set_value(
							"Item",
							challan.get("item_code"),
							"custom_delivery_note",
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
					return error_response(
						f"""Receipt Name: {purchase_receipt_status[0][1]},Receipt Number: {purchase_receipt_status[0][4]},Date: {purchase_receipt_status[0][3]}Ready Receipt of Item Code Is not Submitted"""
					)
			else:
				return error_response("No such record exists")

	except Exception as e:
		frappe.db.rollback()
		frappe.logger("Put Delivery Note").exception(e)
		frappe.log_error(title=_("API Error"), message=e)
		return error_response(str(e))





@frappe.whitelist(allow_guest=True)
def get_specific_delivery_note(kwargs):
	name = kwargs.get("name")

	conditions = get_conditions(name)
	
	delivery_note_data = frappe.get_all(
		"Delivery Note",
		fields=[
			"name",
			"posting_date",
			"custom_client_name",
			"custom_kun_category",
			"custom_cs_category",
			"custom_bb_category",
			"custom_ot_category",
			"custom_is_barcode",
			"docstatus",
		],
		filters={"name": name},
		as_list=False,
	)
	# return delivery_note_data

	if delivery_note_data:
		delivery_note_items = frappe.get_all(
			"Delivery Note Item",
			fields=[
				"idx",
				"item_code",
				"custom_kun_wt",
				"custom_gross_wt",
				"custom_cs_wt",
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
			filters={"parent": name},  # Assuming 'name' is the Delivery Note name
			order_by="idx ASC",
			as_list=False,
		)

		# Add Delivery Note Items data to the Delivery Note data
		delivery_note_data[0]["items"] = delivery_note_items
		for i in delivery_note_data[0]["items"]:
			custom_wt = frappe.db.get_value(
				"Item",
				i.item_code,
				[
					"custom_kun_wt",
					"custom_cs_wt",
					"custom_bb_wt",
					"custom_other_wt",
				],
			)
			i["custom_pr_kun_wt"] = custom_wt[0]
			i["custom_pr_cs_wt"] = custom_wt[1]
			i["custom_pr_bb_wt"] = custom_wt[2]
			i["custom_pr_other_wt"] = custom_wt[3]

		return build_response(
			"success", data=delivery_note_data[0]
		)  # Send success response with combined data
	else:
		return build_response("error", message=_("Delivery Note not found."))

	# except Exception as e:
	# 	frappe.log_error(title=_("Specific Sales"), message=str(e))
	# 	return build_response("error", message=_("An error occurred while fetching data."))


def build_response(status, data=None):
	response = {"status": status}

	if data is not None:
		response["data"] = data

	return response


def get_conditions(name=None):
	conditions = {}
	if name:
		conditions["name"] = name
	return conditions


import frappe
from frappe import _


def build_response(status, data=None, message=None):
	response = {"status": status}

	if data is not None:
		response["data"] = data

	if message is not None:
		response["message"] = message

	return response



@frappe.whitelist(allow_guest=True)
def get_amend_delivery_note(kwargs):
	try:
		data = frappe.db.sql(
			"""
            SELECT
                dn.name,
                dn.custom_client_name,
                dn.custom_kun_category,
                dn.custom_cs_category,
                dn.custom_bb_category,
                dn.custom_ot_category,
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


import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_listening_delivery_note(kwargs):
	try:
		data = frappe.db.sql(
			"""
            SELECT

                dn.name,
                dn.custom_number,
                dn.posting_date,
                dn.custom_client_name,
                dn.docstatus,
                dn.custom_is_barcode
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
def delete_delivery_note_api(kwargs):
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
			# item_doc.save(ignore_permissions=True)

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


@frappe.whitelist(allow_guest=True)
def print_delivery_note_sales(kwargs):
	name = kwargs.get("name")
	# name

	if frappe.db.exists("Delivery Note", name):
		delivery_note_data = frappe.get_doc("Delivery Note", name)
		print_url = f"{frappe.utils.get_url()}/api/method/frappe.utils.print_format.download_pdf?doctype=Delivery%20Note&name={name}&format=Delivery%20Note%20-%20Sales&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en"
		delivery_note_table = {
			"posting_date": delivery_note_data.posting_date,
			"name": delivery_note_data.name,
			"print_url": print_url,
		}

		response_data = {"data": [delivery_note_table]}

		return build_response("success", data=response_data)
	else:
		return build_response("error", message="Purchase Receipt not found")


def build_response(status, data=None, message=None):
	response = {"status": status}
	if data is not None:
		response["data"] = data

	if message is not None:
		response["message"] = message

	return response


import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def get_item_specific_sales(kwargs):
	frappe.db.commit()
	name = kwargs.get("name")
	conditions = get_conditions(name)

	try:
		sql_query = f"""
             SELECT
            item.custom_gross_wt,
            item.custom_warehouse,
            item.custom_kun_wt,
            item.custom_cs_wt,
            item.custom_bb_wt,
            item.custom_other_wt,
            item.custom_kun_pcs

        FROM `tabItem` AS item
            WHERE {conditions}
        """

		data = frappe.db.sql(sql_query, as_dict=True)

		return build_response("success", data=data)
	except Exception as e:
		frappe.log_error(title=_("API Error"), message=str(e))
		return build_response("error", message=_("An error occurred while fetching data."))


def build_response(status, data=None, message=None, exec_time=None, name=None):
	response = {"status": status}

	if data is not None:
		response["data"] = data

	if message is not None:
		response["message"] = message

	if exec_time is not None:
		response["exec_time"] = exec_time

	if name is not None:
		response["name"] = name

	return response


def get_conditions(name=None):
	conditions = ""
	if name:
		conditions += f'item.name = "{name}"'

	return conditions
