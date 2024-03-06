import frappe


@frappe.whitelist(allow_guest=True)
def create_kun_cs_ot_category(kwargs):
    try:
        name1 = kwargs.get("name1")
        type = kwargs.get("type")
        if not name1:
            return error_response("Please define name1")
        if not type:
            return error_response("Please define type")
        kun_category = frappe.new_doc("Kun-CS-Ot Category")
        kun_category.name1 = name1
        kun_category.type = type
        kun_category.save(ignore_permissions=True)
        response_data = {
            "status": "success",
            "message": "Kun-CS-Ot Category Created successfully.",
            "subscribe_id": kun_category.name,
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

        duplicate_entry_index = error_message.find("Duplicate entry")
        if duplicate_entry_index != -1:
            error_message = error_message[duplicate_entry_index:]
        else:
            error_message = (
                "Duplicate entry"  # If specific message not found, use default message
            )

    return {"status": "error", "error": error_message}


@frappe.whitelist(allow_guest=True)
def get_kun_cs_ot_category(kwargs):
    try:
        client = frappe.get_list(
            "Kun-CS-Ot Category",
            fields=["name1", "type"],
            order_by="modified desc",
        )
        return build_response("success", data=client)
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
