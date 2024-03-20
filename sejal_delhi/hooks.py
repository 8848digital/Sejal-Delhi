app_name = "sejal_delhi"
app_title = "sejal_delhi"
app_publisher = "shyam"
app_description = "sejal_delhi"
app_email = "shyamkumar@8848digital.com"
app_license = "MIT"

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/sejal_delhi/css/sejal_delhi.css"
# app_include_js = "/assets/sejal_delhi/js/sejal_delhi.js"

# include js, css files in header of web template
# web_include_css = "/assets/sejal_delhi/css/sejal_delhi.css"
# web_include_js = "/assets/sejal_delhi/js/sejal_delhi.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "sejal_delhi/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "sejal_delhi.utils.jinja_methods",
# 	"filters": "sejal_delhi.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "sejal_delhi.install.before_install"
# after_install = "sejal_delhi.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "sejal_delhi.uninstall.before_uninstall"
# after_uninstall = "sejal_delhi.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "sejal_delhi.utils.before_app_install"
# after_app_install = "sejal_delhi.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "sejal_delhi.utils.before_app_uninstall"
# after_app_uninstall = "sejal_delhi.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "sejal_delhi.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"sejal_delhi.tasks.all"
# 	],
# 	"daily": [
# 		"sejal_delhi.tasks.daily"
# 	],
# 	"hourly": [
# 		"sejal_delhi.tasks.hourly"
# 	],
# 	"weekly": [
# 		"sejal_delhi.tasks.weekly"
# 	],
# 	"monthly": [
# 		"sejal_delhi.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "sejal_delhi.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "sejal_delhi.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "sejal_delhi.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["sejal_delhi.utils.before_request"]
# after_request = ["sejal_delhi.utils.after_request"]

# Job Events
# ----------
# before_job = ["sejal_delhi.utils.before_job"]
# after_job = ["sejal_delhi.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"sejal_delhi.auth.validate"
# ]


doc_events = {
	"Item": {
		"before_save": "sejal_delhi.doc_events.item.validate",
       
	},
	"Purchase Receipt": {
		"autoname": "sejal_delhi.doc_events.purchase_receipt.autoname",
		"validate": "sejal_delhi.doc_events.purchase_receipt.number_set",
	},
	"Delivery Note": {
		"autoname": "sejal_delhi.doc_events.delivery_note.autoname",
		"validate": "sejal_delhi.doc_events.purchase_receipt.number_set",
	},
}

fixtures = [
	{
		"dt": "Custom Field","filters": [["module", "in", ["sejal_delhi"]]],
	},
	{
        "dt": "Property Setter", "filters": [["module", "in", ["sejal_delhi"]]],
    },
    {
        "dt": "Report", "filters": [["module", "in", ["sejal_delhi"]]],
    },
]