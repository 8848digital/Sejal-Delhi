import frappe
from sejal_delhi.utils import success_response, error_response
from sejal_delhi.api.V1 import V1

import time

@frappe.whitelist(allow_guest=True)
def api(**kwargs):
    try:
        st = time.time()
        version = kwargs.get('version') 
        if version == "v1":
            api = V1()
        elif version =="v2":
            api = V2()
        response = api.class_map(kwargs)
        et = time.time()
        if type(response) == dict:
            response['exec_time'] = f"{round(et - st, 4)} seconds"
        return response
    except Exception as e:
        frappe.logger("registration").exception(e)
        return error_response(e)