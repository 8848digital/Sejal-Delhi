// Copyright (c) 2024, shyam and contributors
// For license information, please see license.txt
/* eslint-disable */

frappe.query_reports["Stock Entry"] = {
	"filters": [
		{
			fieldname: "name",
			label: __("Name"),
			fieldtype: "Link",
			options: "Item",
		},
		{
			fieldname: "",
			label: __("Karigar"),
			fieldtype: "Link",
			options: "karigar",
		},


	]
};
