from mimetypes import guess_type
import frappe
import json
from frappe.model.naming import make_autoname
from frappe.utils.image import optimize_image
import requests

#Create Purchase Receipt
@frappe.whitelist(allow_guest=True)
def create_purchase_receipt(kwargs):
	if frappe.request.method == "POST" and frappe.request.data:
		table_data = {}
		data = json.loads(frappe.request.data)
		purchase_receipt = frappe.new_doc("Purchase Receipt")
		purchase_receipt.remarks = data["remarks"]

		get_warehouse_and_karigar(purchase_receipt, data)

		if data.get("items"):
			process_items_without_delivery_note_refno(data, purchase_receipt, table_data)
		
		purchase_receipt.insert(ignore_permissions=True)
		create_purchase_receipt_item_breakup_detail(purchase_receipt, table_data, data)

		return build_response("success", f"Purchase Receipt {purchase_receipt.name} created successfully")

def get_warehouse_and_karigar(purchase_receipt, data):
	custom_ready_receipt_type = data.get("custom_ready_receipt_type")
	warehouse = frappe.db.get_value(
		"Warehouse", {"custom_store_location": data.get("store_location")}, ["name"]
	)
	purchase_receipt.set_warehouse = warehouse
	if custom_ready_receipt_type in ["Kundan", "Mangalsutra"]:
		purchase_receipt.custom_ready_receipt_type = custom_ready_receipt_type
	else:
		purchase_receipt.custom_ready_receipt_type = "Kundan"
	karigar_exist = frappe.db.sql(
		f'''select name from `tabKarigar` where karigar_name="{data['custom_karigar']}"'''
	)
	if karigar_exist:
		purchase_receipt.custom_karigar = karigar_exist[0][0]
	else:
		sup = frappe.get_doc(
			{
				"doctype": "Karigar",
				"karigar_name": data["custom_karigar"],
			}
		).insert(ignore_permissions=True)
		purchase_receipt.custom_karigar = sup.name

def process_items_without_delivery_note_refno(data, purchase_receipt, table_data):
	for row in data["items"]:
		if '-' in row["product_code"]:
			if row["product_code"][:3].isalpha() and row["product_code"][3] == '-' and row["product_code"][4:].isdigit():
				kun_karigar = get_kun_karigar_details(row)
				create_item_from_data(row)

				purchase_receipt_item_details(purchase_receipt, row, kun_karigar)

				item_breakup_detail = "table"
				append_item_breakup_detail(table_data, row, item_breakup_detail)

			else:
				return {"error": "Item Code length should be 3"}
		else:
			if len(row["product_code"]) == 3 and row["product_code"].isalpha():
				kun_karigar = get_kun_karigar_details(row)
				create_item_from_data(row)

				purchase_receipt_item_details(purchase_receipt, row, kun_karigar)

				item_breakup_detail = "table"
				append_item_breakup_detail(table_data, row, item_breakup_detail)

			else:
				return {"error": "Item Code length should be 3"}

def create_purchase_receipt_item_breakup_detail(purchase_receipt, table_data, data):
	for d in purchase_receipt.items:
		purchase_item_breakup = frappe.new_doc("Purchase Receipt Item Breakup")
		purchase_item_breakup_name = make_autoname("Purchase Receipt Item-" + d.item_code + "-.#", "", purchase_item_breakup)
		purchase_item_breakup.name = purchase_item_breakup_name
		purchase_item_breakup.purchase_receipt_item = d.name
		item_doc = frappe.get_doc("Item", d.item_code)
		item_doc.custom_purchase_receipt = purchase_receipt.name
		all_table_data = table_data[d.item_code]
		for t in all_table_data:

			material, material_abbr = check_material_exists(t)
			create_purchase_item_breakup_detail(purchase_item_breakup, material_abbr, material, data, item_doc, t)

		purchase_item_breakup.insert(ignore_permissions=True)

		if not data.get("delivery_note_ref_no"):
			item_doc.save(ignore_permissions=True)

		frappe.db.set_value(
			"Purchase Receipt Item",
			d.name,
			"custom_purchase_receipt_item_breakup",
			purchase_item_breakup.name,
		)

def create_purchase_item_breakup_detail(purchase_item_breakup, material_abbr, material, data, item_doc, t):
	purchase_item_breakup.append(
	"purchase_receipt_item_breakup_detail",
		{
			"material_abbr": material_abbr,
			"material": material,
			"pcs": t["pcs"],
			"piece_": t["piece_"],
			"carat": t["carat"],
			"weight": t["weight"],
			"gm_": t["gm_"],
			"amount": t["amount"],
		},
	)

def append_item_breakup_detail(table_data, row, item_breakup_detail):
	for table_row in row[item_breakup_detail]:
		if not table_data.get(row["product_code"]):
			table_data[row["product_code"]] = [table_row]
		else:
			table_data[row["product_code"]].append(table_row)

def create_item_from_data(row):
	product_code = row["product_code"].upper()
	item = frappe.new_doc("Item")
	if '-' in product_code:
		item_name = product_code
		item.name = product_code
	else:
		item_name = make_autoname(product_code + "-.#", "", item)
		item.name = item_name
	item.item_code = item_name
	item.stock_uom = "Nos"
	item.item_group = "All Item Groups"
	if row.get("custom_kun_karigar"):
		item.custom_kun_karigar = row.get("custom_kun_karigar")
	item.custom_net_wt = row.get("custom_net_wt")
	item.custom_few_wt = row.get("custom_few_wt")
	item.custom_gross_wt = row.get("custom_gross_wt")
	item.custom_mat_wt = row.get("custom_mat_wt")
	item.custom_other = row.get("custom_other")
	item.custom_total = row.get("custom_total")
	item.custom_add_photo = row["custom_add_photo"]

	for item_detail in row["table"]:
		item.append(
		"custom_purchase_receipt_item_breakup_detail",
		{
			"material_abbr": item_detail["material_abbr"], 
			"material": item_detail["material"],
			"pcs": item_detail["pcs"],
			"piece_": item_detail["piece_"],
			"carat": item_detail["carat"],
			"weight": item_detail["weight"],
			"gm_": item_detail["gm_"],
			"amount": item_detail["amount"],
		}
		)
	item.insert(ignore_permissions=True)
	row["product_code"] = item.name


def purchase_receipt_item_details(purchase_receipt, row, kun_karigar):
	purchase_receipt.append(
		"items",
		{
			"item_code": row["product_code"],
			"custom_kun_karigar": kun_karigar,
			"custom_net_wt": row["custom_net_wt"],
			"custom_few_wt": row["custom_few_wt"],
			"custom_gross_wt": row["custom_gross_wt"],
			"custom_mat_wt": row["custom_mat_wt"],
			"custom_other": row["custom_other"],
			"custom_total": row["custom_total"],
			"custom_add_photo": row["custom_add_photo"],
		},
	)

def get_kun_karigar_details(row):
	if row['custom_kun_karigar']:
		kun_karigar_exist = frappe.db.exists("Kundan Karigar", {"karigar_name": row['custom_kun_karigar']})

		if kun_karigar_exist:
			kun_karigar = row['custom_kun_karigar']
		else:
			kun_karigar_doc = frappe.get_doc(
				{
					"doctype": "Kundan Karigar",
					"karigar_name": row["custom_kun_karigar"],
				}
			).insert(ignore_permissions=True)
			kun_karigar = kun_karigar_doc.name
	else:
		kun_karigar = ""
	return kun_karigar

def check_material_exists(t):
	material_exist = frappe.db.sql(
		f'''select name,abbr from `tabMaterial` where material_name="{t['material']}"'''
	)
	if material_exist:
		material = material_exist[0][0]
		material_abbr = material_exist[0][1]
	else:
		material = ""
		material_abbr = ""
		if t["material"]:
			material_doc = frappe.get_doc(
				{
					"doctype": "Material",
					"material_name": t["material"],
					"abbr": t["material_abbr"],
				}
			).insert(ignore_permissions=True)
			material = material_doc.name
			material_abbr = material_doc.abbr
		else:
			pass
	return material, material_abbr


@frappe.whitelist(allow_guest=True)
def get_item_code_details_from_mumbai_site(kwargs):
	try:
		delivery_note_ref_no = kwargs.get("delivery_note_ref_no")
		settings = frappe.get_doc('Sejal Settings')
		sejal_mumbai_app_url = settings.sejal_mumbai_app_url
		dn_url = sejal_mumbai_app_url + "/api/resource/Delivery Note/" + delivery_note_ref_no
		api_key = settings.api_key
		api_secret = settings.api_secret
		headers = {
			'Authorization': f'token {api_key}:{api_secret}',
		}

		dn_response = requests.get(dn_url, headers=headers)
		if dn_response:
			delivery_note_detail = dn_response.json()
			delivery_note_item_detail = delivery_note_detail["data"]["items"]
			all_item_codes = [item["item_code"] for item in delivery_note_item_detail]
			item_list = []
			for item_code in all_item_codes:
				item_code_url = sejal_mumbai_app_url + "/api/resource/Item/" + item_code
				item_code_response = requests.get(item_code_url, headers=headers)
				item_code_detail = item_code_response.json()
				item_list.append(item_code_detail["data"])
			
			extracted_data = []
			for index, item in enumerate(item_list, start=1):
				extracted_item = {
					"idx": index,
					"product_code": item["item_code"],
					"custom_kun_karigar": item["custom_kun_karigar"],
					"custom_net_wt": item["custom_net_wt"],
					"custom_few_wt": item["custom_few_wt"],
					"custom_gross_wt": item["custom_gross_wt"],
					"custom_mat_wt": item["custom_mat_wt"],
					"custom_other": item["custom_other"],
					"custom_total": item["custom_total"],
					"custom_add_photo": item["custom_add_photo"],
					"table": [
					{
						"idx": detail["idx"],
						"material_abbr": detail["material_abbr"],
						"material": detail["material"],
						"pcs": detail["pcs"],
						"piece_": detail["piece_"],
						"carat": detail["carat"],
						"carat_": detail["carat_"],
						"weight": detail["weight"],
						"gm_": detail["gm_"],
						"amount": detail["amount"]
					}
					for detail in item["custom_purchase_receipt_item_breakup_detail"]
				]
				}
				extracted_data.append(extracted_item)

			return build_response("success", extracted_data)
		else:
			return {"Error" : "Delivery Note does not exist"}
	except Exception as e:
		frappe.log_error(message=str(e))
		return build_response("error", message=_("An error occurred while fetching data."))

@frappe.whitelist(allow_guest=True)
def get_delivery_notes_from_mumbai_site(kwargs):
	settings = frappe.get_doc('Sejal Settings')
	sejal_mumbai_app_url = settings.sejal_mumbai_app_url
	dn_url = sejal_mumbai_app_url + "/api/resource/Delivery Note"
	api_key = settings.api_key
	api_secret = settings.api_secret
	headers = {
		'Authorization': f'token {api_key}:{api_secret}',
	}
	
	dn_response = requests.get(dn_url, headers=headers)
	if dn_response:
		delivery_note_detail = dn_response.json()
		delivery_note_list = [item["name"] for item in delivery_note_detail["data"]]
		delivery_note_list_docstatus_one = []
		for dn in delivery_note_list:
			dn_detail_url = sejal_mumbai_app_url + "/api/resource/Delivery Note/" + dn
			dn_detail_response = requests.get(dn_detail_url, headers=headers)
			dn_detail = dn_detail_response.json()
			if dn_detail["data"]["docstatus"] == 1:
				delivery_note_list_docstatus_one.append(dn)
		purchase_receipt = frappe.db.sql("""
							SELECT pr.custom_delivery_note_ref_no FROM `tabPurchase Receipt` AS pr
							""", as_dict=True)
		purchase_receipt_list = [item["custom_delivery_note_ref_no"] for item in purchase_receipt]
		for dn in delivery_note_list_docstatus_one:
			if dn in purchase_receipt_list:
				delivery_note_list_docstatus_one.remove(dn)
		return build_response("success", delivery_note_list_docstatus_one)
	else:
		return {"Error" : "Delivery Note does not exist"}


def error_response(err_msg):
	return {"status": "error", "message": err_msg}

def item_autoname(doc, method):
	pass


@frappe.whitelist(allow_guest=True)
def upload_image(dt=None, dn=None):
	attach_file = frappe.request.files.get("file")
	if attach_file:
		content = attach_file.stream.read()
		filename = attach_file.filename
		content_type = guess_type(filename)[0]
		args = {"content": content, "content_type": content_type}
		content = optimize_image(**args)

		file_doc = frappe.get_doc(
			{
				"doctype": "File",
				"attached_to_doctype": dt,
				"attached_to_name": dn,
				"file_name": filename,
				"is_private": 0,
				"content": content,
			}
		).insert(ignore_permissions=1)

		return file_doc


import frappe
from frappe import _
from frappe.utils.response import build_response


@frappe.whitelist(allow_guest=True)
def get_listening_purchase_receipt(kwargs):
	custom_ready_receipt_type = kwargs.get("custom_ready_receipt_type")
	conditions = get_conditions(custom_ready_receipt_type)
	try:
		data = frappe.db.sql(
			f"""
      SELECT
                pr.custom_number,
                pr.name,
                pr.posting_date,
                pr.custom_ready_receipt_type,
                pr.custom_karigar,
                pr.docstatus
            FROM
                `tabPurchase Receipt` AS pr
        WHERE
            (pr.docstatus = 0 or pr.docstatus = 1 or pr.docstatus = 2)
            AND pr.name NOT IN (SELECT amended_from FROM `tabPurchase Receipt` WHERE amended_from IS NOT NULL)
             {conditions}
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


def get_conditions(custom_ready_receipt_type=None):
	conditions = ""
	if custom_ready_receipt_type:
		conditions += f' AND pr.custom_ready_receipt_type ="{custom_ready_receipt_type}" '

	return conditions


import frappe
from frappe import _
from collections import OrderedDict


# Define the get_conditions function
def get_conditions(name=None):
	conditions = ""
	if name:
		conditions += f' AND pr.name = "{name}"'
	return conditions


# Define the build_response function
def build_response(status, data=None, message=None):
	response = {"status": status, "data": data}

	if message:
		response["message"] = message

	return response


# Define your endpoint function
@frappe.whitelist(allow_guest=True)
def get_name_specific_purchase_receipt(kwargs):
	name = kwargs.get("name")

	conditions = get_conditions(name)
	try:
		data = frappe.db.sql(
			f"""
            SELECT
                pr.name as receipt_name,
                pr.idx as receipt_idx,
                pr.custom_karigar,
                pr.remarks,
                pr.docstatus,
                pr.custom_ready_receipt_type,
                pr.posting_date,
                pr.set_warehouse,
                pri.name as item_name,
                pri.idx  item_idx,
                pri.item_code,
                pri.custom_kun_karigar,
                pri.custom_net_wt,
                pri.custom_few_wt,
                pri.custom_gross_wt,
                pri.custom_mat_wt,
                pri.custom_other,
                pri.custom_total,
                pri.custom_add_photo,
                pri.custom_purchase_receipt_item_breakup,
                pribd.idx as pribd_idx ,
                pribd.name as detail_name,
                pribd.material_abbr,
                pribd.material,
                pribd.pcs,
                pribd.piece_,
                pribd.carat,
                pribd.carat_,
                pribd.weight,
                pribd.gm_,
                pribd.amount
            FROM
                `tabPurchase Receipt` AS pr
            LEFT JOIN `tabPurchase Receipt Item` AS pri ON pri.parent = pr.name
            LEFT JOIN `tabPurchase Receipt Item Breakup` AS prib ON pri.custom_purchase_receipt_item_breakup = prib.name
            LEFT JOIN `tabPurchase Receipt Item Breakup Detail` AS pribd ON prib.name = pribd.parent

            WHERE
                (pr.docstatus = 0 or pr.docstatus = 1 or pr.docstatus = 2)
                AND pr.name NOT IN (SELECT amended_from FROM `tabPurchase Receipt` WHERE amended_from IS NOT NULL)
                {conditions}
            ORDER BY
                item_idx ASC,
                pribd_idx ASC


        """,
			as_dict=True,
		)

		grouped_data = get_grouped_data(data)
		
		final_data = list(grouped_data.values())
		for receipt_data in final_data:
			receipt_data["items"] = list(receipt_data["items"].values())
			for item_data in receipt_data["items"]:
				item_data["table"] = list(item_data["table"])

		return build_response("success", final_data)
	except Exception as e:
		frappe.log_error(message=str(e))
		return build_response("error", message=_("An error occurred while fetching data."))

def get_grouped_data(data):
	grouped_data = OrderedDict()
	for row in data:
		receipt_name = row["receipt_name"]
		item_name = row["item_name"]

		if receipt_name not in grouped_data:
			grouped_data[receipt_name] = {
				"name": receipt_name,
				"custom_karigar": row["custom_karigar"],
				"remarks": row["remarks"],
				"docstatus": row["docstatus"],
				"custom_ready_receipt_type": row["custom_ready_receipt_type"],
				"posting_date": row["posting_date"],
				"set_warehouse": row["set_warehouse"],
				"items": {},
			}

		if item_name not in grouped_data[receipt_name]["items"]:
			grouped_data[receipt_name]["items"][item_name] = {
				"idx": row["item_idx"],  # Add 'item_idx' here
				"product_code": row["item_code"],
				"custom_kun_karigar": row["custom_kun_karigar"],
				"custom_net_wt": row["custom_net_wt"],
				"custom_few_wt": row["custom_few_wt"],
				"custom_gross_wt": row["custom_gross_wt"],
				"custom_mat_wt": row["custom_mat_wt"],
				"custom_other": row["custom_other"],
				"custom_total": row["custom_total"],
				"custom_add_photo": row["custom_add_photo"],
				"custom_purchase_receipt_item_breakup": row[
					"custom_purchase_receipt_item_breakup"
				],
				"table": [],
			}

		table_entry = {
			"idx": len(grouped_data[receipt_name]["items"][item_name]["table"]) + 1,
			"idx": row["pribd_idx"],
			"material_abbr": row["material_abbr"],
			"material": row["material"],
			"pcs": row["pcs"],
			"piece_": row["piece_"],
			"carat": row["carat"],
			"carat_": row["carat_"],
			"weight": row["weight"],
			"gm_": row["gm_"],
			"amount": row["amount"],
		}

		grouped_data[receipt_name]["items"][item_name]["table"].append(table_entry)
	return grouped_data

import frappe
from frappe import _
from frappe.utils.response import build_response
import json
from datetime import date
from frappe.model.naming import *


@frappe.whitelist(allow_guest=True)
def build_response(status, data=None, message=None):
	response = {"status": status}
	if data is not None:
		response["data"] = data
	if message is not None:
		response["message"] = message
	return response


@frappe.whitelist(allow_guest=True)
def put_purchase_receipt(kwargs):
	if frappe.request.method == "PUT":
		data = json.loads(frappe.request.data)
		try:
			if frappe.db.exists("Purchase Receipt", data["name"]):
				purchase_receipt = frappe.get_doc("Purchase Receipt", data["name"])
				# Ensure Karigar exists
				if not frappe.db.exists("Karigar", data["custom_karigar"]):
					doc = frappe.get_doc(
						{
							"doctype": "Karigar",
							"karigar_name": data["custom_karigar"],
						}
					)
					doc.insert(ignore_permissions=True)
				purchase_receipt.custom_karigar = data["custom_karigar"]
				purchase_receipt.remarks = data["remarks"]
				purchase_receipt.custom_ready_receipt_type = data["custom_ready_receipt_type"]

				for i in purchase_receipt.items:
					frappe.delete_doc(
						"Purchase Receipt Item Breakup",
						i.custom_purchase_receipt_item_breakup,
						force=1,
						for_reload=True,
					)
				purchase_receipt.items = []
				item_code_list = frappe.db.get_list("Item", pluck="name")
				for row in data["items"]:
					if (
						row["product_code"] in item_code_list
						and "-" in row["product_code"]
						and len(row["product_code"].split("-")[0]) == 3
					) or (
						"-" not in row["product_code"] and len(row["product_code"]) == 3
					):
						if not row["idx"]:
							frappe.throw("Please Enter a valid idx")
						if frappe.db.exists("Item", row["product_code"]):
							item_code = row["product_code"]

						else:
							new_item_code = make_autoname(row["product_code"] + "-.#")
							new_product = frappe.get_doc(
								{
									"doctype": "Item",
									"item_name": new_item_code,
									"item_code": new_item_code,
									"item_group": "All Item Groups",
									# Other fields for the new item creation
								}
							)
							# return new_item_code
							new_product.insert(ignore_permissions=True)
							item_code = new_item_code
						# update image in item
						frappe.db.set_value(
							"Item",
							item_code,
							"custom_add_photo",
							row.get("custom_add_photo"),
						)
						frappe.db.set_value(
							"Item", item_code, "custom_kun_karigar", row.get("custom_kun_karigar")
						)
						frappe.db.set_value("Item", item_code, "custom_net_wt", row.get("custom_net_wt"))
						frappe.db.set_value("Item", item_code, "custom_mat_wt", row.get("custom_mat_wt"))
						frappe.db.set_value("Item", item_code, "custom_other", row.get("custom_other"))
						frappe.db.set_value("Item", item_code, "custom_total", row.get("custom_total"))
						frappe.db.set_value(
							"Item", item_code, "custom_gross_wt", row.get("custom_gross_wt")
						)
						frappe.db.set_value(
							"Item", item_code, "custom_purchase_receipt", purchase_receipt.name
						)
						# If there is inconsistency, use frappe.db.commit() after updating the image in the Item.
						rec = next(
							(rec for rec in purchase_receipt.items if rec.idx == row.get("idx")),
							None,
						)
						rec_entry = {
							"idx": row["idx"],
							"item_code": item_code,
							"item_group": "All Item Groups",
							"custom_kun_karigar": row.get("custom_kun_karigar", ""),
							"custom_net_wt": row.get("custom_net_wt", 0.0),
							"custom_few_wt": row.get("custom_few_wt", 0.0),
							"custom_gross_wt": row.get("custom_gross_wt", 0.0),
							"custom_mat_wt": row.get("custom_mat_wt", 0.0),
							"custom_other": row.get("custom_other", 0.0),
							"custom_total": row.get("custom_total", 0.0),
							"custom_add_photo": row.get("custom_add_photo"),
							"custom_purchase_receipt_item_breakup": row.get(
								"custom_purchase_receipt_item_breakup"
							),
						}
						if rec:
							rec.update(rec_entry)
						else:
							purchase_receipt.append("items", rec_entry)
							purchase_receipt.save()
							purchase_item_breakup = frappe.get_doc(
								{
									"doctype": "Purchase Receipt Item Breakup",
									"purchase_receipt_item": purchase_receipt.items[
										len(purchase_receipt.items) - 1
									].name,
								}
							)
							purchase_item_breakup.insert()
							purchase_receipt.items[
								len(purchase_receipt.items) - 1
							].custom_purchase_receipt_item_breakup = purchase_receipt.items[
								len(purchase_receipt.items) - 1
							].name
							purchase_receipt.save()
							rec = purchase_receipt.items[len(purchase_receipt.items) - 1]
						if rec.custom_purchase_receipt_item_breakup:
							purchase_item_breakup = frappe.get_doc("Purchase Receipt Item Breakup", rec.name)
							item_doc = frappe.get_doc("Item", item_code)
							item_doc.custom_purchase_receipt_item_breakup_detail = []
							purchase_item_breakup.purchase_receipt_item_breakup_detail = []
							table = row["table"]
							for i in table:
								material_name = i.get("material", None)
								if material_name:
									if not frappe.db.exists("Material", material_name):
										new_material = frappe.get_doc(
											{
												"doctype": "Material",
												"material_name": material_name,
											}
										)
										new_material.insert(ignore_permissions=True)
								child_entry = {
									"material_abbr": i.get("material_abbr"),
									"material": material_name,
									"pcs": i.get("pcs"),
									"piece_": i.get("piece_"),
									"carat": i.get("carat"),
									"carat_": i.get("carat_"),
									"weight": i.get("weight"),
									"gm_": i.get("gm_"),
									"amount": i.get("amount"),
								}
								existing_child_entry = next(
									(
										child
										for child in purchase_item_breakup.purchase_receipt_item_breakup_detail
										if child.idx == i.get("idx")
									),
									None,
								)
								if existing_child_entry:
									existing_child_entry.update(child_entry)
								else:
									purchase_item_breakup.append(
										"purchase_receipt_item_breakup_detail", child_entry
									)
									item_doc.append(
										"custom_purchase_receipt_item_breakup_detail",
										child_entry,
									)
								purchase_item_breakup.save()
					else:
						return {
							"Error": "Product Code length should be 3 / Product Code not present in Item list"
						}
				item_doc.save()
				purchase_receipt.save()
				frappe.db.commit()
				return purchase_receipt
			else:
				return "No such record exists"
		except Exception as e:
			frappe.db.rollback()
			frappe.logger("Put Purchase Receipt").exception(e)
			frappe.log_error(title=_("API Error"), message=e)
			return e


@frappe.whitelist(allow_guest=True)
def print_purchase_receipt_kundan(kwargs):
	name = kwargs.get("name")
	# name
	if frappe.db.exists("Purchase Receipt", name):
		purchase_receipt_data = frappe.get_doc("Purchase Receipt", name)
		print_url = f"{frappe.utils.get_url()}/api/method/frappe.utils.print_format.download_pdf?doctype=Purchase%20Receipt&name={name}&format=Purchase%20Receipt%20-%20Kundan&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en"
		purchase_receipt_table = {
			"posting_date": purchase_receipt_data.posting_date,
			"name": purchase_receipt_data.name,
			"print_url": print_url,
		}

		response_data = {"data": [purchase_receipt_table]}

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


@frappe.whitelist(allow_guest=True)
def print_purchase_receipt_mangalsutra(kwargs):
	name = kwargs.get("name")
	# name
	if frappe.db.exists("Purchase Receipt", name):
		purchase_receipt_data = frappe.get_doc("Purchase Receipt", name)
		print_url = f"{frappe.utils.get_url()}/api/method/frappe.utils.print_format.download_pdf?doctype=Purchase%20Receipt&name={name}&format=Purchase%20Receipt%20-%20Mangalsutra&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en"
		purchase_receipt_table = {
			"posting_date": purchase_receipt_data.posting_date,
			"name": purchase_receipt_data.name,
			"print_url": print_url,
		}

		response_data = {"data": [purchase_receipt_table]}

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


@frappe.whitelist(allow_guest=True)
def delete_purchase_receipt(kwargs):
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

	if frappe.db.exists("Purchase Receipt", name):
		try:
			frappe.delete_doc("Purchase Receipt", name)
			response_data = {
				"message": f"Purchase Receipt {name} deleted successfully.",
				"status": "success",
			}
		except Exception as e:
			response_data = {"message": str(e), "status": "error"}
	else:
		response_data = {
			"message": f"Purchase Receipt {name} not found.",
			"status": "error",
		}

	return response_data


# your_app_name/api.py
import frappe
from frappe import _
from frappe.utils.response import build_response


@frappe.whitelist(allow_guest=True)
def get_specific_kundan_purchase_receipt(kwargs):
	try:
		custom_ready_receipt_type = kwargs.get("custom_ready_receipt_type")
		filters = {}
		if custom_ready_receipt_type:
			filters["custom_ready_receipt_type"] = custom_ready_receipt_type

		# Add your condition to the filters
		filters["docstatus"] = ["in", [0, 1, 2]]
		filters["name"] = [
			"not in",
			frappe.db.sql_list(
				"""SELECT amended_from FROM `tabPurchase Receipt`
                                                         WHERE amended_from IS NOT NULL"""
			),
		]

		our_application = frappe.get_list(
			"Purchase Receipt",
			filters=filters,
			fields=[
				"name",
				"custom_number",
				"posting_date",
				"custom_karigar",
				"custom_ready_receipt_type",
				"docstatus",
			],
			order_by="modified desc",
		)

		return build_response("success", data=our_application)
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