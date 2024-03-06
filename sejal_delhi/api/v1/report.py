import frappe
from frappe import _
# Report

@frappe.whitelist(allow_guest=True)
def get_item_status_report(kwargs):
    name = kwargs.get("name")
    voucher_no = kwargs.get("voucher_no")
    from_date = kwargs.get("from_date")
    to_date = kwargs.get("to_date")
    conditions = "WHERE 1=1"
    if name:
        conditions += f' AND item.name = "{name}"'
    if voucher_no:
        conditions += f' AND sle.voucher_no = "{voucher_no}"'
    fromdate = frappe.utils.getdate(from_date).strftime("%Y-%m-%d")
    todate = frappe.utils.getdate(to_date).strftime("%Y-%m-%d")
    if from_date and to_date:
        conditions += f' AND sle.posting_date BETWEEN "{fromdate}" AND "{todate}"'
    if name and from_date and to_date:
        conditions += f' AND item.name = "{name}" AND sle.posting_date BETWEEN "{fromdate}" AND "{todate}"'
    if name and voucher_no:
        conditions += f' AND item.name ="{name}" AND sle.voucher_no ="{voucher_no}"'
    if name and from_date and to_date:
        conditions += f'AND item.name = "{name}" AND sle.posting_date BETWEEN "{fromdate}" AND "{todate}" '
    if voucher_no and from_date and to_date:
        conditions += f'AND sle.voucher_no = "{voucher_no}" AND sle.posting_date BETWEEN "{fromdate}" AND "{todate}"  '
    if name and from_date and to_date and voucher_no:
        conditions += f'AND item.name = "{name}" AND sle.posting_date BETWEEN "{todate}" AND "{todate}" AND sle.voucher_no = "{voucher_no}" '

    try:
        data = frappe.db.sql(
            f"""
            SELECT DISTINCT
        sle.posting_date,
        sle.voucher_no,
        CASE WHEN sle.actual_qty = 1 THEN sle.actual_qty ELSE 0 END AS in_qty,
        CASE WHEN sle.actual_qty = -1 THEN sle.actual_qty ELSE 0 END AS out_qty,
        CASE WHEN sle.actual_qty = 1 THEN 1 ELSE 0 END AS in_stock_value,
        -- Other fields related to Purchase Receipt
        pri.custom_net_wt as net_wt ,
        pri.custom_few_wt,
        pri.custom_gross_wt,
        pri.custom_mat_wt,
        pri.custom_other,
        pri.custom_total,
        -- Other fields related to Delivery Note (when is_return is 0)
        CASE WHEN dn.is_return = 0 THEN dni.custom_kun_wt END AS custom_kun_wt,
        CASE WHEN dn.is_return = 0 THEN dni.custom_net_wt END AS custom_net_wt,
        CASE WHEN dn.is_return = 0 THEN dni.custom_cs_wt END AS custom_cs_wt,
        CASE WHEN dn.is_return = 0 THEN dni.custom_bb_wt END AS custom_bb_wt,
        CASE WHEN dn.is_return = 0 THEN dni.custom_other_wt END AS custom_other_wt,
        CASE WHEN dn.is_return = 0 THEN dni.custom_cs END AS custom_cs,
        CASE WHEN dn.is_return = 0 THEN dni.custom_cs_amt END AS custom_cs_amt,
        CASE WHEN dn.is_return = 0 THEN dni.custom_kun_pc END AS custom_kun_pc,
        CASE WHEN dn.is_return = 0 THEN dni.custom_kun END AS custom_kun,
        CASE WHEN dn.is_return = 0 THEN dni.custom_kun_amt END AS custom_kun_amt,
        CASE WHEN dn.is_return = 0 THEN dni.custom_ot_ END AS custom_ot_,
        CASE WHEN dn.is_return = 0 THEN dni.custom_ot_amt END AS custom_ot_amt,
        CASE WHEN dn.is_return = 0 THEN dni.custom_other END AS custom_other,
        CASE WHEN dn.is_return = 0 THEN dni.custom_amount END AS custom_amount
        FROM `tabStock Ledger Entry` AS sle
        LEFT JOIN `tabItem` AS item ON sle.item_code = item.name
        LEFT JOIN `tabPurchase Receipt` AS pr ON item.custom_purchase_receipt = pr.name AND sle.voucher_no = pr.name
        LEFT JOIN `tabPurchase Receipt Item` AS pri ON pri.parent = pr.name
        LEFT JOIN `tabDelivery Note` AS dn ON sle.voucher_no = dn.name
        LEFT JOIN `tabDelivery Note Item` AS dni ON dni.parent = dn.name AND sle.voucher_no = dn.name
        {conditions}
        AND (dn.is_return IS NULL OR dn.is_return = 0)
        UNION ALL
        SELECT DISTINCT
        sle.posting_date,
        sle.voucher_no,
        CASE WHEN sle.actual_qty = 1 THEN sle.actual_qty ELSE 0 END AS in_qty,
        CASE WHEN sle.actual_qty = -1 THEN sle.actual_qty ELSE 0 END AS out_qty,
        CASE WHEN sle.actual_qty = 1 THEN 1 ELSE 0 END AS in_stock_value,
        0 AS net_wt,
        0 AS custom_few_wt,
        0 AS custom_gross_wt,
        0 AS custom_mat_wt,
        0 AS custom_other,
        0 AS custom_total,
        dni.custom_kun_wt,
        dni.custom_net_wt,
        dni.custom_cs_wt,
        dni.custom_bb_wt,
        dni.custom_other_wt,
        dni.custom_cs,
        dni.custom_cs_amt,
        dni.custom_kun_pc,
        dni.custom_kun,
        dni.custom_kun_amt,
        dni.custom_ot_,
        dni.custom_ot_amt,
        dni.custom_other,
        dni.custom_amount
        FROM `tabStock Ledger Entry` AS sle
        LEFT JOIN `tabItem` AS item ON sle.item_code = item.name
        LEFT JOIN `tabPurchase Receipt` AS pr ON item.custom_purchase_receipt = pr.name AND sle.voucher_no = pr.name
        LEFT JOIN `tabDelivery Note` AS dn ON sle.voucher_no = dn.name
        LEFT JOIN `tabDelivery Note Item` AS dni ON dni.parent = dn.name AND sle.voucher_no = dn.name
        {conditions}
        AND dn.is_return = 1
            """,
            as_dict=True,
        )
        return build_response("success", data=data)
    except Exception as e:
        frappe.log_error(title=_("API Error"), message=str(e), traceback=True)
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









@frappe.whitelist(allow_guest=True)
def get_daily_qty_status_report(kwargs):
    custom_karigar = kwargs.get("custom_karigar")
    from_date = kwargs.get("from_date")
    to_date = kwargs.get("to_date")
    # condition_pr, condition_dn, condition_pr1, condition_dn1 = get_conditions(custom_karigar, from_date, to_date)
    fromdate = frappe.utils.getdate(from_date).strftime("%Y-%m-%d")
    todate = frappe.utils.getdate(to_date).strftime("%Y-%m-%d")
    condition_pr = ""
    condition_dn = ""
    condition_pr1 = ""
    condition_dn1 = ""
    if custom_karigar and not from_date and not to_date:
        condition_pr += f"AND pr.custom_karigar != '{custom_karigar}'"
        condition_dn += f"AND dn.custom_client_name != '{custom_karigar}'"
        condition_pr1 += f"AND pr.custom_karigar = '{custom_karigar}'"
        condition_dn1 += f"AND dn.custom_client_name = '{custom_karigar}'"
    if from_date and not custom_karigar and not to_date:
        condition_pr += f"AND pr.posting_date < '{fromdate}'"
        condition_dn += f"AND dn.posting_date < '{fromdate}'"
        condition_pr1 += f"AND pr.posting_date >= '{fromdate}'"
        condition_dn1 += f"AND dn.posting_date >= '{fromdate}'"
    if from_date and to_date and not custom_karigar:
        condition_pr += f"AND pr.posting_date < '{fromdate}'"
        condition_dn += f"AND dn.posting_date < '{fromdate}'"
        condition_pr1 += f"AND pr.posting_date BETWEEN '{fromdate}' AND '{todate}'"
        condition_dn1 += f"AND dn.posting_date BETWEEN '{fromdate}' AND '{todate}'"
    # return condition_pr, condition_dn, condition_pr1, condition_dn1
    
    opening_balance_query = ""
    if (from_date and not to_date and not custom_karigar) or (from_date and to_date and not custom_karigar) or (custom_karigar and not from_date and not to_date):
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
    try:
        data = frappe.db.sql(f"""
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
            NULL AS sales_net_weight,
            NULL AS sales_gross_weight,
            NULL AS dn_pcs
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
        """,
            as_dict=True)
        # return data
        return build_response("success", data=data)
    except Exception as e:
        frappe.log_error(title=_("daily Qty"), message=str(e))
        return build_response(
            "error", message=_("An error occurred while fetching data.")
        )


@frappe.whitelist(allow_guest=True)
def print_report_daily_qty_status(kwargs):
    custom_karigar = kwargs.get("custom_karigar")
    from_date = kwargs.get("from_date")
    to_date = kwargs.get("to_date")

    try:
        # Construct print URL
        if custom_karigar is None or from_date is None or to_date is None :
            print_url = f"{frappe.utils.get_url()}/api/method/sj_antique.sj_antique.report.daily_qty_status.daily_qty_status.report"
        if custom_karigar is not None:
            print_url = f"{frappe.utils.get_url()}/api/method/sj_antique.sj_antique.report.daily_qty_status.daily_qty_status.report?custom_karigar={custom_karigar}"
        if from_date is not None:
            print_url = f"{frappe.utils.get_url()}/api/method/sj_antique.sj_antique.report.daily_qty_status.daily_qty_status.report?from_date={from_date}"   
        if to_date is not None:
            print_url = f"{frappe.utils.get_url()}/api/method/sj_antique.sj_antique.report.daily_qty_status.daily_qty_status.report?to_date={to_date}"         
        if custom_karigar is not None and from_date is not None:
            print_url = f"{frappe.utils.get_url()}/api/method/sj_antique.sj_antique.report.daily_qty_status.daily_qty_status.report?custom_karigar={custom_karigar}&from_date={from_date}"   
        if custom_karigar is not None and to_date is not None:
            print_url = f"{frappe.utils.get_url()}/api/method/sj_antique.sj_antique.report.daily_qty_status.daily_qty_status.report?custom_karigar={custom_karigar}&to_date={to_date}"   
        if from_date is not None and to_date is not None:
            print_url = f"{frappe.utils.get_url()}/api/method/sj_antique.sj_antique.report.daily_qty_status.daily_qty_status.report?from_date={from_date}&to_date={to_date}"   
        if custom_karigar is not None and from_date is not None and to_date is not None:
            print("All parameters are present.",custom_karigar,from_date,to_date)
            print_url = f"{frappe.utils.get_url()}/api/method/sj_antique.sj_antique.report.daily_qty_status.daily_qty_status.report?custom_karigar={custom_karigar}&from_date={from_date}&to_date={to_date}"
        return build_response("success", data={"print_url": print_url})
    except Exception as e:
        return frappe.logger("Report").exception(e)

        
    

def get_conditions(custom_karigar, from_date, to_date):
    try:
        conditions = ""
        conditionsdn = ""
        if custom_karigar:
            conditions += f'AND pr.custom_karigar = "{custom_karigar}" '
            conditionsdn += f'AND dn.custom_client_name = "{custom_karigar}"'

        fromdate = frappe.utils.getdate(from_date).strftime("%Y-%m-%d")
        todate = frappe.utils.getdate(to_date).strftime("%Y-%m-%d")
        if from_date and to_date:
            conditions += f'AND pr.posting_date BETWEEN "{fromdate}" AND "{todate}" '
            conditionsdn += f'AND dn.posting_date BETWEEN "{fromdate}" AND "{todate}" '

        if custom_karigar and from_date and to_date:
            conditions += f'AND pr.custom_karigar = "{custom_karigar}" AND pr.posting_date BETWEEN "{fromdate}"AND "{todate}"'

        return conditions, conditionsdn
    except Exception as e:
        frappe.logger("Report").exception(e)

def build_response(status, data=None, message=None):
    response = {"status": status}

    if data is not None:
        response["data"] = data

    if message is not None:
        response["message"] = message

    return response
