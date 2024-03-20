import frappe
from sejal_delhi.utils import success_response, error_response
import sejal_delhi.api.v1.access_token as access_token
import sejal_delhi.api.v1.karigar as karigar
import sejal_delhi.api.v1.kundan_karigar as kundan_karigar
import sejal_delhi.api.v1.material as material
import sejal_delhi.api.v1.material_group as material_group
import sejal_delhi.api.v1.client as client
import sejal_delhi.api.v1.client_group as client_group
import sejal_delhi.api.v1.kun_cs_ot_category as kun_cs_ot_category
import sejal_delhi.api.v1.bb_category as bb_category
import sejal_delhi.api.v1.warehouse_list as warehouse_list
import sejal_delhi.api.v1.purchase_receipt as purchase_receipt
import sejal_delhi.api.v1.sales as sales
import sejal_delhi.api.v1.sales_return as sales_return
import sejal_delhi.api.v1.report as report
import sejal_delhi.api.v1.barcode as barcode


class V1:
	def __init__(self):
		self.methods = {
			"access_token": ["get_access_token"],
			"karigar": ["create_karigar", "get_karigar"],
			"kundan_karigar": ["create_kundan_karigar", "get_kundan_karigar"],
			"material": ["create_material", "get_material"],
			"material_group": ["create_material_group", "get_material_group"],
			"client": ["create_client", "get_client"],
			"client_group": ["create_client_group", "get_client_group"],
			"kun_cs_ot_category": [
				"create_kun_cs_ot_category",
				"get_kun_cs_ot_category",
			],
			"bb_category": ["create_bb_category", "get_bb_category"],
			"warehouse_list": ["get_warehouse_list", "get_warehouse_list"],
			"purchase_receipt": [
				"create_purchase_receipt",
				"get_listening_purchase_receipt",
				"get_name_specific_purchase_receipt",
				"put_purchase_receipt",
				"print_purchase_receipt_kundan",
				"print_purchase_receipt_mangalsutra",
				"delete_purchase_receipt",
				"get_specific_kundan_purchase_receipt",
				"get_item_code_details_from_mumbai_site",
				"get_delivery_notes_from_mumbai_site",
			],
			"sales": [
				"create_delivery_note",
				"get_delivery_note",
				"put_delivery_note",
				"get_specific_delivery_note",
				"get_amend_delivery_note",
				"get_listening_delivery_note",
				"delete_delivery_note_api",
				"print_delivery_note_sales",
				"get_item_specific_sales",
			],
			"sales_return": [
				"create_delivery_note_sales_return",
				"get_specific_delivery_note_sales_return",
				"put_delivery_note_sales_return",
				"get_delivery_note_specific_return_item",
				"get_listening_delivery_note_sales_return",
				"delete_delivery_note_sales_return",
			],
			"report": [
				"get_item_status_report",
				"get_daily_qty_status_report",
				"print_report_daily_qty_status",
				"product_code_report",
			],
			"barcode": [
				"get_barcode",
				"create_barcode",
				"get_item_wise_barcode_filter",
				"get_item_specific_barcode",
				"get_specific_barcode_detail",
				"print_barcode",
				"get_multiple_specific_print_barcode",
				"get_karigar_and_client_name",
			],
		}

	def class_map(self, kwargs):
		entity = kwargs.get("entity")
		method = kwargs.get("method")
		if self.methods.get(entity):
			if method in self.methods.get(entity):
				function = f"{kwargs.get('entity')}.{kwargs.get('method')}({kwargs})"
				return eval(function)
			else:
				return error_response("Method Not Found!")
		else:
			return error_response("Entity Not Found!")
