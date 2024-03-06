import frappe


@frappe.whitelist(allow_guest=True)
def create_material_group(kwargs):
    try:
        material_group = kwargs.get(
            "material_group"
        )  # Use 'material' key for material name
        if not material_group:
            return error_response("Please define material_group")
        applicant = frappe.new_doc("Material Group")
        applicant.material_group = material_group
        applicant.save(ignore_permissions=True)
        response_data = {
            "status": "success",
            "message": "Material Created successfully.",
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


import frappe
from frappe import _
from frappe.utils.response import build_response


@frappe.whitelist(allow_guest=True)
def get_material_group(kwargs):
    try:
        our_application = frappe.get_list(
            "Material Group",
            fields=["material_group"],
            order_by="modified desc",
        )
        renamed_data = []
        for material_info in our_application:
            renamed_data.append({"material_group": material_info.get("material_group")})
        return build_response("success", data=renamed_data)
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
