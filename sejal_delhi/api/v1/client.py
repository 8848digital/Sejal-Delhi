import frappe


# Post Cliet API
@frappe.whitelist(allow_guest=True)
def create_client(kwargs):
    try:
        client_name = kwargs.get("client_name")
        client_group = kwargs.get("client_group")
        if not client_name:
            return error_response("Please define client_name")
        if not client_group:
            return error_response("Please define client_group")
        if not frappe.db.exists("Client Group", client_group):
            client = frappe.new_doc("Client Group")
            client.client_group = client_group
            client.insert(ignore_permissions=True)
        doc = frappe.get_doc(
            {
                "doctype": "Client",
                "client_name": client_name,
                "client_group": client_group,
            }
        )
        doc.insert(ignore_permissions=True)
        response_data = {
            "status": "success",
            "message": "Client created successfully.",
            "client_id": doc.name,
        }
        return {"status": "success", "data": response_data}
    except Exception as e:
        frappe.logger("error").exception(e)
        return error_response(str(e))


def error_response(message):
    return {"status": "failed", "message": message}


# Get Cliet API
@frappe.whitelist(allow_guest=True)
def get_client(kwargs):
    try:
        client = frappe.get_list(
            "Client",
            fields=["client_name", "client_group"],
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
