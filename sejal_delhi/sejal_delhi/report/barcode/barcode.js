frappe.query_reports["Barcode"] = {
    "filters": [
        
        {"label": "Posting Date", "fieldname": "posting_date", "fieldtype": "Date"},
        {"label": "Custom Karigar", "fieldname": "custom_karigar", "fieldtype": "Data"},
        {"label": "Name", "fieldname": "name", "fieldtype": "Data"},
        {"label": "Sr From", "fieldname": "sr_from", "fieldtype": "Int"},
        {"label": "SR To", "fieldname": "sr_to", "fieldtype": "Int"},
        {"label": "Item Code","fieldname": "item_code", "fieldtype": "Select", "options": ["","A", "G"]}
            
            
       
    ]
};