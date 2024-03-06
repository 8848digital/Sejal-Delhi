# your_app_name/api.py
import frappe
from frappe import _
from frappe.utils.response import build_response


@frappe.whitelist(allow_guest=True)
def get_warehouse_list(kwargs):
   
    try:
        our_application = frappe.get_list(
            "Warehouse",
            filters={"custom_store_location": ["!=", ""]},
            fields=["custom_store_location"],
            order_by="modified desc",
        )
        
        return build_response("success", data=our_application)
    except Exception as e:
        frappe.log_error(title=_("API Error"), message=e)
        return build_response(
            "error", message=_("An error occurred while fetching data.")
        )


def build_response(status, data=None, message=None):
    response = {"status": status}

    if data is not None:
        response["data"] = data

    if message is not None:
        response["message"] = message

    return response
