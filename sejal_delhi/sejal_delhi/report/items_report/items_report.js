// Copyright (c) 2024, Deepak Kumar and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Items Report"] = {
	"filters": [
		{
			fieldname: "name",
			label: __("Name"),
			fieldtype: "Link",
			options: "Item",
		},
		{
			fieldname: "custom_karigar",
			label: __("karigar"),
			fieldtype: "Link",
			options: "Karigar",
		}


	]
};
