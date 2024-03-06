import frappe
from frappe import _
from frappe.utils.response import build_response


import frappe


@frappe.whitelist(allow_guest=True)
def create_material(kwargs):
    try:
        data_list = kwargs.get("data", [])
        response_data = []
        for data in data_list:
            material_name = data.get("material")
            abbr = data.get("material_abbr")
            material_group = data.get("material_group")
            if not material_name:
                return error_response("Please define material")
            if not abbr:
                return error_response("Please define material_abbr")
            if not abbr:
                return error_response("Please define material_group")

            applicant = frappe.new_doc("Material")
            applicant.material_name = material_name
            applicant.abbr = abbr
            applicant.material_group = material_group
            applicant.save(ignore_permissions=True)
            response_data.append(
                {
                    "status": "success",
                    "message": "Material Created successfully.",
                    "subscribe_id": applicant.name,
                }
            )

        return {"status": "success", "data": response_data}
    except Exception as e:
        frappe.logger("leave").exception(e)
        return error_response(str(e))


def error_response(err_msg):
    error_message = "Duplicate entry"
    if isinstance(err_msg, tuple) and len(err_msg) >= 3:
        error_message = str(err_msg[2])
        duplicate_entry_index = error_message.find("Duplicate entry")
        if duplicate_entry_index != -1:
            error_message = error_message[duplicate_entry_index:]
        else:
            error_message = "Duplicate entry"

    return {"status": "error", "error": error_message}


@frappe.whitelist(allow_guest=True)
def create_material_group(kwargs):
    try:
        material_group = kwargs.get("material_group")
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
    error_message = "Duplicate entry"
    if isinstance(err_msg, tuple) and len(err_msg) >= 3:
        error_message = str(err_msg[2])
        duplicate_entry_index = error_message.find("Duplicate entry")
        if duplicate_entry_index != -1:
            error_message = error_message[duplicate_entry_index:]
        else:
            error_message = "Duplicate entry"

    return {"status": "error", "error": error_message}


@frappe.whitelist(allow_guest=True)
def get_material(kwargs):
    try:
        our_application = frappe.get_list(
            "Material",
            fields=["material_name", "abbr", "material_group"],
            order_by="modified desc",
        )
        renamed_data = []
        for material_info in our_application:
            renamed_data.append(
                {
                    "material": material_info.get("material_name"),
                    "material_abbr": material_info.get("abbr"),
                    "material_group": material_info.get("material_group"),
                }
            )

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

        # Renaming the keys in the response dictionary
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
