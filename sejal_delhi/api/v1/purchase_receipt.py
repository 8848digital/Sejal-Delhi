from mimetypes import guess_type
import frappe
import json
from frappe.model.naming import make_autoname
from frappe.utils.image import optimize_image

# Creates
@frappe.whitelist(allow_guest=True)
def create_purchase_receipt(kwargs):
	try:
		if frappe.request.method == "POST" and frappe.request.data:
			data = json.loads(frappe.request.data)
			purchase_receipt = frappe.new_doc("Purchase Receipt")
			purchase_receipt.remarks = data["remarks"]
			# purchase_receipt.remarks = data['custom_ready_receipt_type']
			custom_ready_receipt_type = data.get("custom_ready_receipt_type")
			# get warehouse based on store location
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
			table_data = {}
			for row in data["items"]:
				if len(row["product_code"]) == 3:
					product_code = row["product_code"]
					item = frappe.new_doc("Item")
					item_name = make_autoname(product_code + "-.#", "", item)
					item.name = item_name
					item.item_code = item_name
					item.stock_uom = "Nos"
					item.item_group = "All Item Groups"
					item.custom_kun_karigar = row.get("custom_kun_karigar")
					item.custom_net_wt = row.get("custom_net_wt")
					item.custom_few_wt = row.get("custom_few_wt")
					item.custom_gross_wt = row.get("custom_gross_wt")
					item.custom_mat_wt = row.get("custom_mat_wt")
					item.custom_other = row.get("custom_other")
					item.custom_total = row.get("custom_total")
					item.custom_add_photo = row["custom_add_photo"]
					item.insert(ignore_permissions=True)
					row["product_code"] = item.name
					kun_karigar_exist = frappe.db.sql(
						f'''select name from `tabKundan Karigar` where karigar_name="{row['custom_kun_karigar']}"'''
					)

					if kun_karigar_exist:
						kun_karigar = kun_karigar_exist[0][0]
					else:
						kun_karigar = ""
						if not row["custom_kun_karigar"]:
							pass

						else:
							kun_karigar_doc = frappe.get_doc(
								{
									"doctype": "Kundan Karigar",
									"karigar_name": row["custom_kun_karigar"],
								}
							).insert(ignore_permissions=True)
							kun_karigar = kun_karigar_doc.name
					# PR item child table
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
					frappe.db.commit()
					for table_row in row["table"]:
						if not table_data.get(row["product_code"]):
							table_data[row["product_code"]] = [table_row]
						else:
							table_data[row["product_code"]].append(table_row)
				else:
					return {"error": "Product Code length should be 3"}
			purchase_receipt.insert(ignore_permissions=True)
			# child table breakup create
			for d in purchase_receipt.items:
				# return table_data
				purchase_item_breakup = frappe.new_doc("Purchase Receipt Item Breakup")
				purchase_item_breakup.purchase_receipt_item = d.name
				# get the item doc
				item_doc = frappe.get_doc("Item", d.item_code)
				# set purchase receipt in item
				item_doc.custom_purchase_receipt = purchase_receipt.name
				all_table_data = table_data[d.item_code]
				for t in all_table_data:
					# Create Material if not exist
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
					purchase_item_breakup.append(
						"purchase_receipt_item_breakup_detail",
						{
							"material_abbr": material_abbr,
							"material": material,
							"pcs": t["pcs"],
							"piece_": t["piece_"],
							"carat": t["carat"],
							"carat_": t["carat_"],
							"weight": t["weight"],
							"gm_": t["gm_"],
							"amount": t["amount"],
						},
					)

					# add data to item breakup table
					item_doc.append(
						"custom_purchase_receipt_item_breakup_detail",
						{
							"material_abbr": material_abbr,
							"material": material,
							"pcs": t["pcs"],
							"piece_": t["piece_"],
							"carat": t["carat"],
							"carat_": t["carat_"],
							"weight": t["weight"],
							"gm_": t["gm_"],
							"amount": t["amount"],
						},
					)
				purchase_item_breakup.insert(ignore_permissions=True)
				item_doc.save(ignore_permissions=True)
				frappe.db.set_value(
					"Purchase Receipt Item",
					d.name,
					"custom_purchase_receipt_item_breakup",
					purchase_item_breakup.name,
				)

			# frappe.delete_doc("Item", data['item_code'])
			frappe.db.commit()
			return {"message": f"{purchase_receipt.name}"}
	except Exception as e:
		frappe.logger("Create Purchase").exception(e)
		return error_response(str(e))


# except Exception as e:
#     frappe.logger('PurchaseReceipt').exception(e)
# return error_response(str(e))


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

		final_data = list(grouped_data.values())
		for receipt_data in final_data:
			receipt_data["items"] = list(receipt_data["items"].values())
			for item_data in receipt_data["items"]:
				item_data["table"] = list(item_data["table"])

		# return final_data
		# returb value come

		return build_response("success", final_data)
	except Exception as e:
		frappe.log_error(message=str(e))
		return build_response("error", message=_("An error occurred while fetching data."))


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