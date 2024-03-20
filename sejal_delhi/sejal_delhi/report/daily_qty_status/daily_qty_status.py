import frappe
import json
import pdfkit
from io import BytesIO
from datetime import datetime
from frappe import _
def execute(filters=None):
    columns, data = [], []
    return columns, data
def difference(values):
    # Calculate the difference between the last two values
    return values[-1] - values[-2] if len(values) >= 2 else None
def execute(filters=None):
    columns = [
    {
        "label": _("Name"),
        "fieldname": "name",
        "fieldtype": "Data",
        "width": 150
    },
    {
        "label": _("Net Weight"),
        "fieldname": "net_weight",
        "fieldtype": "Data",
        "width": 150
    },
    {
        "label": _("Gross Weight"),
        "fieldname": "gross_weight",
        "fieldtype": "Data",
        "width": 150
    },
    {
        "label": _("PR Pcs"),
        "fieldname": "pr_pcs",
        "fieldtype": "Data",
        "width": 150
    },
    {
        "label": _("Sales Net Weight"),
        "fieldname": "sales_net_weight",
        "fieldtype": "Data",
        "width": 150
    },
    {
        "label": _("Sales Gross Weight"),
        "fieldname": "sales_gross_weight",
        "fieldtype": "Data",
        "width": 150
    },
    {
        "label": _("DN Pcs"),
        "fieldname": "dn_pcs",
        "fieldtype": "Data",
        "width": 150
    }
    ]
    condition_pr = ""
    condition_dn = ""
    condition_pr1 = ""
    condition_dn1 = ""
    if filters and 'custom_karigar' in filters:
        condition_pr += "AND pr.custom_karigar != %(custom_karigar)s"
        condition_dn += "AND dn.custom_client_name != %(custom_karigar)s"
        condition_pr1 += "AND pr.custom_karigar = %(custom_karigar)s"
        condition_dn1 += "AND dn.custom_client_name = %(custom_karigar)s"
    if filters and 'from_date' in filters:
        condition_pr += "AND pr.posting_date < %(from_date)s"
        condition_dn += "AND dn.posting_date < %(from_date)s"
        condition_pr1 += "AND pr.posting_date >= %(from_date)s"
        condition_dn1 += "AND dn.posting_date >= %(from_date)s"
    if filters and 'to_date' in filters:
        condition_pr += "AND pr.posting_date < %(to_date)s"
        condition_dn += "AND dn.posting_date < %(to_date)s"
        condition_pr1 += "AND pr.posting_date <= %(to_date)s"
        condition_dn1 += "AND dn.posting_date <= %(to_date)s"
    if (filters and 'from_date' in filters) and (filters and 'to_date' in filters):
        condition_pr += "AND pr.posting_date < %(from_date)s"
        condition_dn += "AND dn.posting_date < %(from_date)s"
        condition_pr1 += "AND pr.posting_date BETWEEN %(from_date)s AND %(to_date)s"
        condition_dn1 += "AND dn.posting_date BETWEEN %(from_date)s AND %(to_date)s"
   
    
    opening_balance_query = ""
    if ((filters and 'from_date' in filters) and not (filters and 'to_date' in filters) and not (filters and 'custom_karigar' in filters)) or ((filters and 'from_date' in filters) and (filters and 'to_date' in filters) and not (filters and 'custom_karigar' in filters) ) or ((filters and 'custom_karigar' in filters) and not (filters and 'from_date' in filters) and not (filters and 'to_date' in filters)):
        opening_balance_query = f"""
            SELECT
            'Opening Balance' AS name,
            COALESCE(SUM(net_weight), 0) AS net_weight,
            COALESCE(SUM(gross_weight), 0) AS gross_weight,
            COALESCE(SUM(pr_pcs), 0) AS pr_pcs,
            COALESCE(SUM(sales_net_weight), 0) AS sales_net_weight,
            COALESCE(SUM(sales_gross_weight), 0) AS sales_gross_weight,
            COALESCE(SUM(dn_pcs), 0) AS dn_pcs
        FROM (
            SELECT 
            combined_data.custom_karigar AS name,
            combined_data.total_net_wt AS net_weight,
            combined_data.total_gross_wt AS gross_weight,
            combined_data.total_qty AS pr_pcs,
            COALESCE(sales_data.sales_net_weight, 0) AS sales_net_weight, 
            COALESCE(sales_data.sales_gross_weight, 0) AS sales_gross_weight,
            COALESCE(sales_data.total_qty, 0) AS dn_pcs
        FROM (
            SELECT 
                custom_karigar, 
                SUM(custom_net_wt)+SUM(custom_few_wt) AS total_net_wt, 
                SUM(custom_gross_wt) AS total_gross_wt,
                SUM(total_qty) AS total_qty
                
            FROM (
                SELECT 
                    pr.custom_karigar AS custom_karigar, 
                    pri.custom_net_wt,
                    pri.custom_few_wt,
                    pri.custom_gross_wt,
                    pr.total_qty
                FROM `tabPurchase Receipt` AS pr
                LEFT JOIN `tabPurchase Receipt Item` AS pri ON pri.parent = pr.name
                WHERE pr.docstatus = 1 {condition_pr}

                UNION ALL

                SELECT 
                    dn.custom_client_name AS custom_karigar, 
                    dni.custom_net_wt,
                    NULL AS custom_net_wt,
                    dni.custom_gross_wt,
                    ABS(dn.total_qty) AS total_qty 
                FROM `tabDelivery Note` AS dn
                LEFT JOIN `tabDelivery Note Item` AS dni ON dni.parent = dn.name
                WHERE dn.is_return = 1 AND dn.docstatus = 1 {condition_dn}
            ) AS combined_data
            GROUP BY custom_karigar
        ) AS combined_data
        LEFT JOIN (
            SELECT 
                dn.custom_client_name AS custom_karigar,
                SUM(dni.custom_net_wt) AS sales_net_weight,
                SUM(dni.custom_gross_wt) AS sales_gross_weight,
                SUM(ABS(dn.total_qty)) AS total_qty
            FROM `tabDelivery Note` AS dn
            LEFT JOIN `tabDelivery Note Item` AS dni ON dni.parent = dn.name
            WHERE dn.is_return = 0 AND dn.docstatus = 1 {condition_dn}
            GROUP BY dn.custom_client_name
        ) AS sales_data ON combined_data.custom_karigar = sales_data.custom_karigar
        ) AS subquery

        UNION ALL"""
    else:
        opening_balance_query = f"""
            SELECT
            'Opening Balance' AS name,
            COALESCE(SUM(net_weight)-SUM(net_weight), 0) AS net_weight,
            COALESCE(SUM(gross_weight)-SUM(gross_weight), 0) AS gross_weight,
            COALESCE(SUM(pr_pcs)-SUM(pr_pcs), 0) AS pr_pcs,
            COALESCE(SUM(sales_net_weight)-SUM(sales_net_weight), 0) AS sales_net_weight,
            COALESCE(SUM(sales_gross_weight)-SUM(sales_gross_weight), 0) AS sales_gross_weight,
            COALESCE(SUM(dn_pcs)-SUM(dn_pcs), 0) AS dn_pcs
        FROM (
            SELECT 
            combined_data.custom_karigar AS name,
            combined_data.total_net_wt AS net_weight,
            combined_data.total_gross_wt AS gross_weight,
            combined_data.total_qty AS pr_pcs,
            COALESCE(sales_data.sales_net_weight, 0) AS sales_net_weight, 
            COALESCE(sales_data.sales_gross_weight, 0) AS sales_gross_weight,
            COALESCE(sales_data.total_qty, 0) AS dn_pcs
        FROM (
            SELECT 
                custom_karigar, 
                SUM(custom_net_wt)+SUM(custom_few_wt) AS total_net_wt, 
                SUM(custom_gross_wt) AS total_gross_wt,
                SUM(total_qty) AS total_qty
                
            FROM (
                SELECT 
                    pr.custom_karigar AS custom_karigar, 
                    pri.custom_net_wt,
                    pri.custom_few_wt,
                    pri.custom_gross_wt,
                    pr.total_qty
                FROM `tabPurchase Receipt` AS pr
                LEFT JOIN `tabPurchase Receipt Item` AS pri ON pri.parent = pr.name
                WHERE pr.docstatus = 1 {condition_pr}

                UNION ALL

                SELECT 
                    dn.custom_client_name AS custom_karigar, 
                    dni.custom_net_wt,
                    NULL AS custom_net_wt,
                    dni.custom_gross_wt,
                    ABS(dn.total_qty) AS total_qty 
                FROM `tabDelivery Note` AS dn
                LEFT JOIN `tabDelivery Note Item` AS dni ON dni.parent = dn.name
                WHERE dn.is_return = 1 AND dn.docstatus = 1 {condition_dn}
            ) AS combined_data
            GROUP BY custom_karigar
        ) AS combined_data
        LEFT JOIN (
            SELECT 
                dn.custom_client_name AS custom_karigar,
                SUM(dni.custom_net_wt) AS sales_net_weight,
                SUM(dni.custom_gross_wt) AS sales_gross_weight,
                SUM(ABS(dn.total_qty)) AS total_qty
            FROM `tabDelivery Note` AS dn
            LEFT JOIN `tabDelivery Note Item` AS dni ON dni.parent = dn.name
            WHERE dn.is_return = 0 AND dn.docstatus = 1 {condition_dn}
            GROUP BY dn.custom_client_name
        ) AS sales_data ON combined_data.custom_karigar = sales_data.custom_karigar
        ) AS subquery

        UNION ALL"""
   
    mydata = frappe.db.sql(f"""
    {opening_balance_query}

SELECT 
    COALESCE(combined_data.custom_karigar, 0) AS name,
    COALESCE(combined_data.total_net_wt, 0) AS net_weight,
    COALESCE(combined_data.total_gross_wt, 0) AS gross_weight,
    COALESCE(combined_data.total_qty, 0) AS pr_pcs,
    COALESCE(sales_data.sales_net_weight, 0) AS sales_net_weight, 
    COALESCE(sales_data.sales_gross_weight, 0) AS sales_gross_weight,
    COALESCE(sales_data.total_qty, 0) AS dn_pcs
FROM (
    SELECT 
        custom_karigar, 
        SUM(custom_net_wt)+SUM(custom_few_wt) AS total_net_wt, 
        SUM(custom_gross_wt) AS total_gross_wt,
        SUM(total_qty) AS total_qty
        
    FROM (
        SELECT 
            pr.custom_karigar AS custom_karigar, 
            pri.custom_net_wt,
            pri.custom_few_wt,
            pri.custom_gross_wt,
            pr.total_qty
        FROM `tabPurchase Receipt` AS pr
        LEFT JOIN `tabPurchase Receipt Item` AS pri ON pri.parent = pr.name
        WHERE pr.docstatus = 1 {condition_pr1}

        UNION ALL

        SELECT 
            dn.custom_client_name AS custom_karigar, 
            dni.custom_net_wt,
            NULL AS custom_few_wt,
            dni.custom_gross_wt,
            ABS(dn.total_qty) AS total_qty 
        FROM `tabDelivery Note` AS dn
        LEFT JOIN `tabDelivery Note Item` AS dni ON dni.parent = dn.name
        WHERE dn.is_return = 1 AND dn.docstatus = 1 {condition_dn1}
    ) AS combined_data
    GROUP BY custom_karigar
) AS combined_data
LEFT JOIN (
    SELECT 
        dn.custom_client_name AS custom_karigar,
        SUM(dni.custom_net_wt) AS sales_net_weight,
        SUM(dni.custom_gross_wt) AS sales_gross_weight,
        SUM(ABS(dn.total_qty)) AS total_qty
    FROM `tabDelivery Note` AS dn
    LEFT JOIN `tabDelivery Note Item` AS dni ON dni.parent = dn.name
    WHERE dn.is_return = 0 AND dn.docstatus = 1 {condition_dn1}
    GROUP BY dn.custom_client_name
) AS sales_data ON combined_data.custom_karigar = sales_data.custom_karigar

UNION ALL

SELECT
    'Total' AS name,
    SUM(net_weight) AS net_weight,
    SUM(gross_weight) AS gross_weight,
    SUM(pr_pcs) AS pr_pcs,
    SUM(sales_net_weight) AS sales_net_weight,
    SUM(sales_gross_weight) AS sales_gross_weight,
    SUM(dn_pcs) AS dn_pcs
FROM (
    SELECT 
    combined_data.custom_karigar AS name,
    combined_data.total_net_wt AS net_weight,
    combined_data.total_gross_wt AS gross_weight,
    combined_data.total_qty AS pr_pcs,
    COALESCE(sales_data.sales_net_weight, 0) AS sales_net_weight, 
    COALESCE(sales_data.sales_gross_weight, 0) AS sales_gross_weight,
    COALESCE(sales_data.total_qty, 0) AS dn_pcs
FROM (
    SELECT 
        custom_karigar, 
        SUM(custom_net_wt)+SUM(custom_few_wt) AS total_net_wt, 
        SUM(custom_gross_wt) AS total_gross_wt,
        SUM(total_qty) AS total_qty
        
    FROM (
        SELECT 
            pr.custom_karigar AS custom_karigar, 
            pri.custom_net_wt,
            pri.custom_few_wt,
            pri.custom_gross_wt,
            pr.total_qty
        FROM `tabPurchase Receipt` AS pr
        LEFT JOIN `tabPurchase Receipt Item` AS pri ON pri.parent = pr.name
        WHERE pr.docstatus = 1 {condition_pr1}

        UNION ALL

        SELECT 
            dn.custom_client_name AS custom_karigar, 
            dni.custom_net_wt,
            NULL AS custom_few_wt,
            dni.custom_gross_wt,
            ABS(dn.total_qty) AS total_qty 
        FROM `tabDelivery Note` AS dn
        LEFT JOIN `tabDelivery Note Item` AS dni ON dni.parent = dn.name
        WHERE dn.is_return = 1 AND dn.docstatus = 1 {condition_dn1}
    ) AS combined_data
    GROUP BY custom_karigar
) AS combined_data
LEFT JOIN (
    SELECT 
        dn.custom_client_name AS custom_karigar,
        SUM(dni.custom_net_wt) AS sales_net_weight,
        SUM(dni.custom_gross_wt) AS sales_gross_weight,
        SUM(ABS(dn.total_qty)) AS total_qty
    FROM `tabDelivery Note` AS dn
    LEFT JOIN `tabDelivery Note Item` AS dni ON dni.parent = dn.name
    WHERE dn.is_return = 0 AND dn.docstatus = 1 {condition_dn1}
    GROUP BY dn.custom_client_name
) AS sales_data ON combined_data.custom_karigar = sales_data.custom_karigar
) AS subquery

UNION ALL

SELECT
    'Balance' AS name,
    SUM(net_weight) - SUM(sales_net_weight) AS net_weight,
    SUM(gross_weight) - SUM(sales_gross_weight) AS gross_weight,
    SUM(pr_pcs) - SUM(dn_pcs)  AS pr_pcs,
    0 AS sales_net_weight,
    0 AS sales_gross_weight,
    0 AS dn_pcs
FROM (
    SELECT 
    combined_data.custom_karigar AS name,
    combined_data.total_net_wt AS net_weight,
    combined_data.total_gross_wt AS gross_weight,
    combined_data.total_qty AS pr_pcs,
    COALESCE(sales_data.sales_net_weight, 0) AS sales_net_weight, 
    COALESCE(sales_data.sales_gross_weight, 0) AS sales_gross_weight,
    COALESCE(sales_data.total_qty, 0) AS dn_pcs
FROM (
    SELECT 
        custom_karigar, 
        SUM(custom_net_wt)+SUM(custom_few_wt) AS total_net_wt, 
        SUM(custom_gross_wt) AS total_gross_wt,
        SUM(total_qty) AS total_qty
        
    FROM (
        SELECT 
            pr.custom_karigar AS custom_karigar, 
            pri.custom_net_wt,
            pri.custom_few_wt,
            pri.custom_gross_wt,
            pr.total_qty
        FROM `tabPurchase Receipt` AS pr
        LEFT JOIN `tabPurchase Receipt Item` AS pri ON pri.parent = pr.name
        WHERE pr.docstatus = 1 {condition_pr1}

        UNION ALL

        SELECT 
            dn.custom_client_name AS custom_karigar, 
            dni.custom_net_wt,
            NULL AS custom_few_wt,
            dni.custom_gross_wt,
            ABS(dn.total_qty) AS total_qty 
        FROM `tabDelivery Note` AS dn
        LEFT JOIN `tabDelivery Note Item` AS dni ON dni.parent = dn.name
        WHERE dn.is_return = 1 AND dn.docstatus = 1 {condition_dn1}
    ) AS combined_data
    GROUP BY custom_karigar
) AS combined_data
LEFT JOIN (
    SELECT 
        dn.custom_client_name AS custom_karigar,
        SUM(dni.custom_net_wt) AS sales_net_weight,
        SUM(dni.custom_gross_wt) AS sales_gross_weight,
        SUM(ABS(dn.total_qty)) AS total_qty
    FROM `tabDelivery Note` AS dn
    LEFT JOIN `tabDelivery Note Item` AS dni ON dni.parent = dn.name
    WHERE dn.is_return = 0 AND dn.docstatus = 1 {condition_dn1}
    GROUP BY dn.custom_client_name
) AS sales_data ON combined_data.custom_karigar = sales_data.custom_karigar
) AS subquery
        """, filters, as_dict=True)
    return columns, mydata

def get_report_content(mydata,filters=None):
    content = '<html><head><title>Print Format</title><style>body { font-family: Arial, sans-serif; }</style></head><body>'
    content += '<html><head><title>{}</title><style>body {{ font-family: Arial, sans-serif; }}</style></head><body>'.format(
        _("Page {0} of {1}").format('<span class="page"></span>', '<span class="topage"></span>'))
    

    if filters:
        filter_html = '<tr><th colspan="8"></th></tr>'
        for key, value in filters.items():
            parsed_date = datetime.strptime(value, "%Y-%m-%d")
            formatted_date = parsed_date.strftime("%d-%m-%Y")
            filter_html += f'<tr><th></th><th style="width: 10%; font-weight: bold;"><b>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;{key.replace("_", " ").title()}:</b> {formatted_date}  </th></tr>'
        content += filter_html
    content += '<table style="border-collapse: collapse; width: 90%; margin-left: 50px; margin-right: 20px;page-break-inside: avoid;>'
    content += '''
        <tr>
            <th style="border: 1px solid black; width: 10%;"></th>
            <th style="border: 1px solid black; width: 15%;">Name</th>
            <th style="border: 1px solid black; width: 15%;">Net Weight</th>
            <th style="border: 1px solid black; width: 15%;">Gross Weight</th>
            <th style="border: 1px solid black; width: 10%;">Pcs</th>
            <th style="border: 1px solid black; width: 15%;">Sale Net Weight</th>
            <th style="border: 1px solid black; width: 15%;">Sale Gross Weight</th>
            <th style="border: 1px solid black; width: 10%;">Sale Pcs</th>
        </tr>
    '''
    total_gross_weight = 0
    total_net_weight = 0
    total_amount = 0
    for value in mydata:
        category = value.get('name', "")
        net_weight = value.get('net_weight', 0)
        gross_weight = value.get('gross_weight', 0)
        pr_pcs = value.get('pr_pcs', 0)
        sales_net_weight = value.get('sales_net_weight', 0)
        sales_gross_weight = value.get('sales_gross_weight', 0)
        dn_pcs = value.get('dn_pcs', 0)
        if all(v is not None for v in [category, gross_weight, net_weight, pr_pcs, sales_net_weight, sales_gross_weight, dn_pcs]):
            content += f'''
                <tr>
                    <td style="border: 1px solid gray; width: 10%;">{category}</td>
                    <td style="border: 1px solid gray; text-align: right; width: 15%;">{net_weight:.3f}</td>
                    <td style="border: 1px solid gray; text-align: right; width: 15%;">{gross_weight:.3f}</td>
                    <td style="border: 1px solid gray; text-align: right; width: 10%;">{pr_pcs}</td>
                    <td style="border: 1px solid gray; text-align: right; width: 15%;">{sales_net_weight:.3f}</td>
                    <td style="border: 1px solid gray; text-align: right; width: 15%;">{sales_gross_weight:.3f}</td>
                    <td style="border: 1px solid gray; text-align: right; width: 10%;">{dn_pcs}</td>
                </tr>
            '''
# Generate the table rows for the second table
    content += '<tr><td colspan="8" style="height: 100px;"></td></tr>'
    content += '''
        <table style="border-collapse: collapse; width: 90%; margin-left: 50px; margin-right: 20px;page-break-inside: avoid;>
            <tr>
                <th style="border: 1px solid black; width: 10%;"></th>
                <th style="border: 1px solid black; width: 15%;">Name</th>
                <th style="border: 1px solid black; width: 15%;">Net Weight</th>
                <th style="border: 1px solid black; width: 15%;">Gross Weight</th>
                <th style="border: 1px solid black; width: 10%;">Pcs</th>
                <th style="border: 1px solid black; width: 15%;">Sale Net Weight</th>
                <th style="border: 1px solid black; width: 15%;">Sale Gross Weight</th>
                <th style="border: 1px solid black; width: 10%;">Sale Pcs</th>
            </tr>
    '''
    for value in mydata:
        category = value.get('name', "")
        net_weight = value.get('net_weight', 0)
        gross_weight = value.get('gross_weight', 0)
        pr_pcs = value.get('pr_pcs', 0)
        sales_net_weight = value.get('sales_net_weight', 0)
        sales_gross_weight = value.get('sales_gross_weight', 0)
        dn_pcs = value.get('dn_pcs', 0)
        # if all(v is not None for v in [category, gross_weight, net_weight, pr_pcs, sales_net_weight, sales_gross_weight, dn_pcs]):
        if category in ['Total', 'Balance'] and all(v is not None for v in [category, gross_weight, net_weight, pr_pcs, sales_net_weight, sales_gross_weight, dn_pcs]):
            if category == 'Total':
                category = 'Grand Total'
            content += f'''
                <tr>
                    <td style="border: 1px solid gray; width: 10%;">{category}</td>
                    <td style="border: 1px solid gray; text-align: right; width: 15%;">{net_weight:.3f}</td>
                    <td style="border: 1px solid gray; text-align: right; width: 15%;">{gross_weight:.3f}</td>
                    <td style="border: 1px solid gray; text-align: right; width: 10%;">{pr_pcs}</td>
                    <td style="border: 1px solid gray; text-align: right; width: 15%;">{sales_net_weight:.3f}</td>
                    <td style="border: 1px solid gray; text-align: right; width: 15%;">{sales_gross_weight:.3f}</td>
                    <td style="border: 1px solid gray; text-align: right; width: 10%;">{dn_pcs}</td>
                </tr>
            '''
    content += '</table>'
    content += '</body></html>'
    print(content)
    return content
def generate_pdf_from_html(html_content):
    try:
        pdf_content = pdfkit.from_string(html_content, False, options={'page-size': 'Letter'})
        return pdf_content
    except Exception as e:
        frappe.msgprint(f"Error generating PDF: {e}")
        return None
@frappe.whitelist(allow_guest=True)
def report(**kwargs):
    print(kwargs)
    kwargs.pop('cmd', None)

    columns, mydata = execute(filters=kwargs)
    # columns, mydata = execute(filters=filters)
    name = "Daily Qty Status"
    html_content = get_report_content(mydata, kwargs)
    pdf_content = generate_pdf_from_html(html_content)
    frappe.local.response.filename = "{name}.pdf".format(
        name=name.replace(" ", "-").replace("/", "-")
    )
    frappe.local.response.filecontent = pdf_content
    frappe.local.response.type = "pdf"