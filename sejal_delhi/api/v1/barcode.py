# your_app_name/api.py
import frappe
from frappe import _
from frappe.utils.response import build_response
import pdfkit
from datetime import datetime
import jinja2
from jinja2 import Template
import json
import os
from frappe.utils import get_url
import urllib.parse
from frappe.utils.pdf import get_pdf
from frappe.model.naming import make_autoname
from frappe.utils.image import optimize_image


@frappe.whitelist(allow_guest=True)
def get_barcode(kwargs):
	try:
		our_application = frappe.get_list(
			"Barcode",
			fields=[
				"idx",
				"item_code",
				"custom_gross_wt",
				"custom_kun_wt",
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
			],
			order_by="modified desc",
		)
		for i, entry in enumerate(our_application):
			entry["idx"] = i + 1
		return build_response("success", data=our_application)
	except Exception as e:
		frappe.log_error(title=_("API Error"), message=e)
		return build_response("error", message=_("An error occurred while fetching data."))


def build_response(status, data=None, message=None):
	response = {"status": status}

	if data is not None:
		response["data"] = data

	if message is not None:
		response["message"] = message

	return response


# Corrected create_barcodes function
@frappe.whitelist(allow_guest=True)
def create_barcode(kwargs):
	try:
		barcode_data = kwargs.get("data")
		items = []
		for item in barcode_data:
			barcode_item_list = frappe.db.get_list("Barcode", pluck="name")
			if item["item_code"] not in barcode_item_list:
				barcode = frappe.new_doc("Barcode")
				barcode.item_code = item["item_code"]
				barcode.custom_gross_wt = item["custom_gross_wt"]
				barcode.custom_kun_wt = item["custom_kun_wt"]
				barcode.custom_cs_wt = item["custom_cs_wt"]
				barcode.custom_bb_wt = item["custom_bb_wt"]
				barcode.custom_other_wt = item["custom_other_wt"]
				barcode.custom_net_wt = item["custom_net_wt"]
				barcode.custom_cs = item["custom_cs"]
				barcode.custom_cs_amt = item["custom_cs_amt"]
				barcode.custom_kun_pc = item["custom_kun_pcs"]
				barcode.custom_bb_pc = item["custom_bb_pcs"]
				barcode.custom_kun = item["custom_kun"]
				barcode.custom_kun_amt = item["custom_kun_amt"]
				barcode.custom_ot_ = item["custom_ot_"]
				barcode.custom_ot_amt = item["custom_ot_amt"]
				barcode.custom_other = item["custom_other"]
				barcode.custom_amount = item["custom_amount"]
				barcode.save(ignore_permissions=True)
				items.append(barcode.name)
			else:
				barcode = frappe.get_doc("Barcode", item["item_code"])
				barcode.custom_gross_wt = item["custom_gross_wt"]
				barcode.custom_kun_wt = item["custom_kun_wt"]
				barcode.custom_cs_wt = item["custom_cs_wt"]
				barcode.custom_bb_wt = item["custom_bb_wt"]
				barcode.custom_other_wt = item["custom_other_wt"]
				barcode.custom_net_wt = item["custom_net_wt"]
				barcode.custom_cs = item["custom_cs"]
				barcode.custom_cs_amt = item["custom_cs_amt"]
				barcode.custom_kun_pc = item["custom_kun_pcs"]
				barcode.custom_bb_pc = item["custom_bb_pcs"]
				barcode.custom_kun = item["custom_kun"]
				barcode.custom_kun_amt = item["custom_kun_amt"]
				barcode.custom_ot_ = item["custom_ot_"]
				barcode.custom_ot_amt = item["custom_ot_amt"]
				barcode.custom_other = item["custom_other"]
				barcode.custom_amount = item["custom_amount"]
				barcode.save(ignore_permissions=True)
				items.append(barcode.name)
		response_data = {
			"status": "success",
			"message": "Barcode Created successfully.",
		}
		return {"status": "success", "data": response_data, "items": items}
	except Exception as e:
		frappe.logger("leave").exception(e)
		return error_response(str(e))


def error_response(err_msg):
	error_message = "Duplicate entry"  # Default error message
	if isinstance(err_msg, tuple) and len(err_msg) >= 3:
		error_message = str(
			err_msg[2]
		)  # Extracting the specific error message from the tuple
		duplicate_entry_index = error_message.find("Duplicate entry")
		if duplicate_entry_index != -1:
			error_message = error_message[duplicate_entry_index:]
		else:
			error_message = (
				"Duplicate entry"  # If specific message not found, use default message
			)
	return {"status": "error", "error": error_message}


@frappe.whitelist(allow_guest=True)
def get_item_wise_barcode_filter(kwargs):
	try:
		name = kwargs.get("name")
		posting_date = kwargs.get("posting_date")
		custom_karigar = kwargs.get("custom_karigar")
		sr_from = kwargs.get("sr_from")
		sr_to = kwargs.get("sr_to")
		stock = kwargs.get("stock")

		purchase_receipt_conditions = ""
		delivery_note_conditions = ""
		purchase_receipt_filters_list = []
		delivery_note_filters_list = []

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
		if sr_from:
			srfrom = int(sr_from)
			purchase_receipt_filters_list.append(
				f"CAST(SUBSTRING(item_code, 5) AS SIGNED) >= {srfrom}"
			)
			delivery_note_filters_list.append(
				f"CAST(SUBSTRING(item_code, 5) AS SIGNED) >= {srfrom}"
			)
		if sr_to:
			srto = int(sr_to)
			purchase_receipt_filters_list.append(
				f"CAST(SUBSTRING(item_code, 5) AS SIGNED) <= {srto}"
			)
			delivery_note_filters_list.append(
				f"CAST(SUBSTRING(item_code, 5) AS SIGNED) <= {srto}"
			)

		if name:
			purchase_receipt_filters_list.append(f'item_code LIKE "{name}%"')
			delivery_note_filters_list.append(f'item_code LIKE "{name}%"')
		if purchase_receipt_filters_list:
			purchase_receipt_conditions = "AND " + " AND ".join(purchase_receipt_filters_list)
		if delivery_note_filters_list:
			delivery_note_conditions = "AND " + " AND ".join(delivery_note_filters_list)

		if stock == "A":
			query_a = f"""
            SELECT
                'Purchase Receipt' AS source,
                pri.item_code AS item_code,
                pr.idx,
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
            #     dn.idx,
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
		if stock == "G":
			query_a = f"""
            SELECT
                'Delivery Note (Sales)' AS source,
                dni.item_code AS item_code,
                dn.idx,
                dn.posting_date AS posting_date,
                dn.custom_client_name AS custom_karigar
            FROM
                `tabDelivery Note` AS dn
            LEFT JOIN
                `tabDelivery Note Item` AS dni ON dni.parent = dn.name
            WHERE
                dn.is_return = 0 {delivery_note_conditions}
            """
		if stock == None or stock == "":
			query_a = f"""
                SELECT
                    'Purchase Receipt' AS source,
                    pri.item_code AS item_code,
                    pr.posting_date AS posting_date,
                    pr.idx,
                    pr.custom_karigar AS custom_karigar
                FROM
                    `tabPurchase Receipt` AS pr
                LEFT JOIN
                    `tabPurchase Receipt Item` AS pri ON pri.parent = pr.name
                WHERE pr.docstatus = 1 {purchase_receipt_conditions}

				UNION ALL

				SELECT
                'Delivery Note (Sales)' AS source,
                dni.item_code AS item_code,
                dn.idx,
                dn.posting_date AS posting_date,
                dn.custom_client_name AS custom_karigar
            FROM
                `tabDelivery Note` AS dn
            LEFT JOIN
                `tabDelivery Note Item` AS dni ON dni.parent = dn.name
				WHERE dn.docstatus = 1 {delivery_note_conditions}
            """

		data = frappe.db.sql(query_a + query_b + "ORDER BY item_code, idx", as_dict=True)

		idx_counter = {}
		filtered_data = []
		for row in data:
			idx = row["idx"]
			if idx not in idx_counter:
				idx_counter[idx] = 0
			else:
				idx_counter[idx] += 1
			row["idx"] = idx_counter[idx]
			filtered_data.append(row)

		return build_response("success", data=filtered_data)
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
def get_item_specific_barcode(kwargs):
	frappe.db.commit()

	name_list = kwargs.get("name")
	final_list = {}
	for i in name_list:
		items = frappe.db.get_all(
			"Item",
			filters={"name": i},
			fields=[
				"custom_gross_wt",
				"custom_warehouse",
				"custom_kun_wt",
				"custom_cs_wt",
				"custom_bb_wt",
				"custom_other_wt",
				"custom_kun_pcs",
				"custom_bb_pcs",
			],
		)
		# Add item_code to each item in the list
		final_list[i] = [{"item_code": i, **item} for item in items]
	response_data = {
		"data": final_list,
		"status": "success",
		"exec_time": "0.0041 seconds",
	}
	return {"message": response_data}


def get_specific_barcode_detail(kwargs):
	name = kwargs.get("name")
	conditions = ""
	filters = []
	if name:
		filters.append(f'bar.name = "{name}"')
	if filters:
		conditions += "WHERE " + " AND ".join(filters)
	try:
		data = frappe.db.sql(
			f"""
            SELECT
                bar.item_code,
                bar.custom_gross_wt,
                bar.custom_kun_wt,
                bar.custom_cs_wt,
                bar.custom_bb_wt,
                bar.custom_other_wt,
                bar.custom_net_wt,
                bar.custom_cs,
                bar.custom_cs_amt,
                bar.custom_kun_pc,
                bar.custom_kun,
                bar.custom_kun_amt,
                bar.custom_ot_,
                bar.custom_ot_amt,
                bar.custom_other,
                bar.custom_amount


            FROM
                `tabBarcode` as bar

                {conditions}
            ORDER BY
                modified DESC
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


import frappe


@frappe.whitelist(allow_guest=True)
def print_barcode(kwargs):
	name = kwargs.get("name")
	# name

	if frappe.db.exists("Barcode", name):
		barcode = frappe.get_doc("Barcode", name)
		print_url = f"{frappe.utils.get_url()}/api/method/frappe.utils.print_format.download_pdf?doctype=Barcode&name={name}&format=Barcode&no_letterhead=1&letterhead=No%20Letterhead&settings=%7B%7D&_lang=en"
		barcode = {"name": barcode.name, "print_url": print_url}

		response_data = {"data": [barcode]}

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
def get_multiple_specific_print_barcode(kwargs, internal_call=False):
	frappe.db.commit()
	if internal_call:
		name_list = kwargs.get("name", [])
	else:
		name_list = list(eval(kwargs.get("name", [])))
	item_list = []
	if name_list:
		for i in name_list:
			items = frappe.db.get_all(
				"Barcode",
				filters={"name": i},
				fields=[
					"custom_gross_wt",
					"custom_kun_wt",
					"custom_cs_wt",
					"custom_bb_wt",
					"custom_net_wt",
					"custom_other_wt",
					"custom_cs",
					"custom_cs_amt",
					"custom_kun",
					"custom_kun_pc",
					"custom_bb_pc",
					"custom_kun_amt",
					"custom_ot_",
					"custom_other",
					"custom_ot_amt",
					"custom_amount",
				],
			)
			code_list = []
			for item in items:
				code_list.append(i)
				code_list.append(item["custom_gross_wt"])
				code_list.append(item["custom_net_wt"])
				less_wt = item["custom_gross_wt"] - item["custom_net_wt"]
				code_list.append(less_wt)
				code_list.append(item["custom_amount"])
				code_list.append(item["custom_kun_wt"])
				code_list.append(item["custom_cs_wt"])
				code_list.append(item["custom_bb_wt"])
				code_list.append(item["custom_other_wt"])
				code_list.append(item["custom_cs"])
				code_list.append(item["custom_cs_amt"])
				code_list.append(item["custom_kun_pc"])
				code_list.append(item["custom_bb_pc"])
				code_list.append(item["custom_kun"])
				code_list.append(item["custom_kun_amt"])
				code_list.append(item["custom_ot_"])
				code_list.append(item["custom_ot_amt"])
				code_list.append(item["custom_other"])
			item_list.append(code_list)
	if internal_call:
		return item_list
	else:
		response_data = {
			"print_url": "{}/api/method/sj_antique.api.v1.barcode.report?item_list=[{}]".format(
				frappe.utils.get_url(), ",".join(f"'{name}'" for name in name_list)
			),
			"status": "success",
		}
		return response_data


def generate_pdf_from_html(html_content):
	try:
		pdf_content = pdfkit.from_string(
			html_content,
			False,
			options={
				"page-width": "4cm",
				"page-height": "1.4cm",
				"margin-top": "0",
				"margin-bottom": "0",
				"margin-left": "0",
				"margin-right": "0",
			},
		)
		return pdf_content
	except Exception as e:
		frappe.msgprint(f"Error generating PDF: {e}")
		return None


def html_data(item_data):
	html_content = """
    """
	for item_code in item_data:
		html_content += f"""
        <div style="display: flex;justify-content:space-between; page-break-inside: avoid; margin-top: -6px; padding-left:5px; padding-top: 2px;">
            <div >
                <div class="text" style="font-size: 15px; font-weight:600; text-align: right; margin-left:-7px; width:110px; margin-top:-3px !important; margin-bottom:0px !important;">{item_code[0]}</div>
                <div class="text" style="font-size: 13px; font-weight:500; font-family: sans-serif;  margin-left:-7px !important;  margin-top:-6px !important;  ">G:{item_code[1]:.3f} </div>
                <div class="text" style="font-size: 13px; font-weight:500; font-family: sans-serif; margin-top:-3px !important; margin-left:-7px !important; margin-bottom:-3px !important;">N:{item_code[2]:.3f} </div>
                <div class="text" style="font-size: 13px; font-weight:500; font-family: sans-serif; margin-top:-5px !important; margin-left:-7px !important; margin-bottom:-3px !important;">Less Wt:{item_code[3]:.3f}</div>
               <div class="text"  style="font-size: 12px; font-weight:500; font-family: sans-serif; margin-top:-5px !important; margin-left:-7px !important; margin-bottom:-3px !important;">Kun/BB Pcs:{item_code[11]:.0f}/{item_code[12]:.0f}</div>

            </div>
           <div style="padding-right:1px; margin-top:1px; margin-right:-3px;">
                <img style="height: 60px; width: 60px;" src="https://barcode.tec-it.com/barcode.ashx?data={item_code[0]}%09{item_code[1]:.3f}%09{item_code[5]:.3f}%09{item_code[6]:.3f}%09{item_code[7]:.3f}%09{item_code[8]:.3f}%09{item_code[2]:.3f}%09{item_code[9]:.3f}%09{item_code[10]:.2f}%09{item_code[11]:.3f}%09{item_code[12]:.3f}%09{item_code[13]:.2f}%09{item_code[14]:.3f}%09{item_code[15]:.2f}%09{item_code[16]:.3f}%09{item_code[4]:.2f}&code=QRCode" alt="QR Code">
            </div>
        </div>

        """
	return html_content


@frappe.whitelist(allow_guest=True)
def report(item_list):
	item_list = list(eval(item_list))
	item_data = []
	data = {"name": []}
	for item in item_list:
		print(item)
		data["name"].append(item)
	item_data = get_multiple_specific_print_barcode(data, internal_call=True)
	html_content = html_data(item_data)
	pdf_content = generate_pdf_from_html(html_content)
	name = "Barcode"
	if pdf_content:
		frappe.local.response.filename = "{name}.pdf".format(
			name=name.replace(" ", "-").replace("/", "-")
		)
		frappe.local.response.filecontent = pdf_content
		frappe.local.response.type = "pdf"
	return frappe.local.response


@frappe.whitelist(allow_guest=True)
def get_karigar_and_client_name(kwargs):
	try:
		data = []
		purchase_receipt_data = frappe.db.sql(
			"""
            SELECT DISTINCT
                pr.custom_karigar
            FROM
                `tabPurchase Receipt` AS pr
        """
		)
		delivery_note_data = frappe.db.sql(
			"""
            SELECT DISTINCT
                dn.custom_client_name
            FROM
                `tabDelivery Note` AS dn
        """
		)
		for row in purchase_receipt_data:
			data.append(row[0])
		for row in delivery_note_data:
			data.append(row[0])
		unique_data = list(set(data))
		return build_response("success", unique_data)
	except Exception as e:
		frappe.log_error(title=_("API Error"), message=str(e))
		return build_response("error", message=_("An error occurred while fetching data."))
