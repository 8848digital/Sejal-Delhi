import frappe
from frappe.utils import random_string
import requests
from frappe.utils.data import get_url
from frappe.model.db_query import DatabaseQuery


def check_user_exists(email):
	"""
	Check if a user with the provied Email. exists
	"""
	return frappe.db.exists('User', email)


def success_response(data=None, id=None):
	response = {'msg': 'success'}
	response['data'] = data
	if id:
		response['data'] = {'id': id, "name": id}
	return response


def error_response(err_msg):
	# frappe.log_error(frappe.get_traceback(), 'Api Error')
	return {
		'msg': 'error',
		'error': err_msg
	}

def send_mail(template_name, recipients, context):
	frappe.sendmail(
		recipients=recipients,
		subject=frappe.render_template(
			frappe.db.get_value(
				"Email Template", template_name, "subject"
			),
			context,
		),
		cc="",
		bcc="",
		delayed=False,
		message=frappe.render_template(
			frappe.db.get_value(
				"Email Template", template_name, "response"
			),
			context,
		),
		reference_doctype="",
		reference_name="",
		attachments="",
		print_letterhead=False,
	)
	return "Email Sent"

def get_logged_user():
    header = {"Authorization": frappe.request.headers.get('Authorization')}
    response = requests.post(get_url() + "/api/method/frappe.auth.get_logged_user", headers=header)
    user = response.json().get("message")
    return user


def get_field_names(page_type):
    return frappe.db.get_all(
        'Page Fields',
        filters={'parent': frappe.get_value('Product Page', {'page_type': page_type})},
        pluck='field'
    )	

def get_count(doctype, **args):
    try:
        distinct = "distinct " if args.get("distinct") else ""
        args["fields"] = [f"count({distinct}`tab{doctype}`.name) as total_count"]
        res = DatabaseQuery(doctype).execute(**args)
        data = res[0].get("total_count")
        return data
    except Exception as e:
        frappe.logger('project').exception(e)
        return error_response(str(e))