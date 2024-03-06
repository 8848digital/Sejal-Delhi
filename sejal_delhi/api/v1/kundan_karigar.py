import frappe
from frappe import _
from frappe.utils.response import build_response


# Post Kundan Karigar
@frappe.whitelist(allow_guest=True)
def create_kundan_karigar(kwargs):
    try:
        karigar_name = kwargs.get("karigar_name")
        if not karigar_name:
            return error_response("Please define kundan_karigar_name")
        applicant = frappe.new_doc("Kundan Karigar")
        applicant.karigar_name = karigar_name
        applicant.save(ignore_permissions=True)
        response_data = {
            "status": "success",
            "message": "Kundan Karigar Created successfully.",
            "subscribe_id": applicant.name,
        }
        return {"status": "success", "data": response_data}
    except Exception as e:
        frappe.logger("leave").exception(e)
        return error_response(str(e))


def error_response(err_msg):
    error_message = "Duplicate entry"  # Default error message
    if isinstance(err_msg, tuple) and len(err_msg) >= 3:
        error_message = str(
            err_msg[2]
        )  # Extracting the specific error message from the tuple

        # Extracting "Duplicate entry" message if present
        duplicate_entry_index = error_message.find("Duplicate entry")
        if duplicate_entry_index != -1:
            error_message = error_message[duplicate_entry_index:]
        else:
            error_message = (
                "Duplicate entry"  # If specific message not found, use default message
            )

    return {"status": "error", "error": error_message}


# Get-Kundan Karigar
@frappe.whitelist(allow_guest=True)
def get_kundan_karigar(kwargs):
    try:
        our_application = frappe.get_list(
            "Kundan Karigar", fields=["karigar_name"], order_by="modified desc"
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
