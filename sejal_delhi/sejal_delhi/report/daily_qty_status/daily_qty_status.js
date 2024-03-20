// Copyright (c) 2024, shyam and contributors
// For license information, please see license.txt
/* eslint-disable */


frappe.query_reports["Daily Qty Status"] = {
    "filters": [
        {
            fieldname: "custom_karigar",
            label: "Name",
            fieldtype: "Data",
        },
        {
            fieldname: "from_date",
            label: __("From Date"),
            fieldtype: "Date",
        },
        {
            fieldname: "to_date",
            label: __("To Date"),
            fieldtype: "Date",
        },
    ],
    "formatter": function (value, row, column, data, default_formatter) {
        var style = "";
		if (data.name == "Opening Balance") {
			style = "color: Purple;"
		}
        if (data.name == "Total") {
            style = "color: red;";
        } else if (data.name == "Balance") {
            style = "color: blue;";
        }
        return "<div style='" + style + "'>" + default_formatter(value, row, column, data) + "</div>";
    },
        onload: function(report) {
        const downloadButton = $(`<button class="btn btn-primary btn-sm">Print</button>`);
        downloadButton.on('click', function() {
            const filters = frappe.query_report.get_query_params();
            console.log(filters)
            const fromDate = filters.from_date;
            const toDate = filters.to_date;
            let url = `//${window.location.host}/api/method/sejal_delhi.sejal_delhi.report.daily_qty_status.daily_qty_status.report`
            let isFirstParameter = true;
            Object.entries(filters).forEach(([key, value]) => {
                if (isFirstParameter) {
                    url += `?${key}=${value}`;
                    isFirstParameter = false;
                  } else {
                    url += `&${key}=${value}`;
                  }
              });
              console.log(url)
            url = url.replace(/ /g, '%20');
            window.open(url, '_blank');
        });
        $('.page-actions').append(downloadButton);
    },
};