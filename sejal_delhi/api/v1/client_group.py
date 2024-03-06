import frappe


@frappe.whitelist(allow_guest=True)
def create_client_group(kwargs):
    try:
        client_group = kwargs.get(
            "client_group"
        )  # Use 'material' key for material name

        if not client_group:
            return error_response("Please define client_group")

        applicant = frappe.new_doc("Client Group")
        applicant.client_group = client_group

        applicant.save(ignore_permissions=True)

        response_data = {
            "status": "success",
            "message": "Client Group Created successfully.",
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


@frappe.whitelist(allow_guest=True)
def get_client_group(kwargs):
    try:
        client_group = frappe.get_list(
            "Client Group",
            fields=["client_group"],
            order_by="modified desc",
        )
        return build_response("success", data=client_group)
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
