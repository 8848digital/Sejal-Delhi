frappe.query_reports["Items Report"] = {
    "filters": [
        {
            "fieldname": "name",
            "label": __("Name"),
            "fieldtype": "Link",
            "options": "Item",
        },
        {
            "fieldname": "custom_karigar",
            "label": __("Karigar"),
            "fieldtype": "Link",
            "options": "Karigar",
        },
        {
            "fieldname": "custom_warehouse",
            "label": __("Location"),
            "fieldtype": "Link",
            "options": "Warehouse",
        },
        {
            "fieldname": "limit_page_length",
            "label": __("Page Length"),
            "fieldtype": "Select",
            "options": ["10", "20", "50", "100", "500", "ALL"], // Corrected 500 option
            "default": "10",
        },
        {
            "fieldname": "limit_start",
            "label": __("Start"),
            "fieldtype": "Int",
            "default": 0,
        },
    ],
}

var selectedValue = 10;
function execute(value) {
   
    
    frappe.query_report.filters[2].set_value(value); // Update page length filter value
    frappe.query_report.refresh(); // Refresh report with updated filters
}

// Create pagination buttons and append them to the DOM
var div = document.createElement('div');
div.className = 'list-paging-area level';
div.innerHTML = `
    <div class="level-left">
        <div class="btn-group">
            <button type="button" class="btn btn-default btn-sm btn-paging ${selectedValue === 10 ? 'btn-info' : ''}" data-value="10">
                10
            </button>
            <button type="button" class="btn btn-default btn-sm btn-paging ${selectedValue === 20 ? 'btn-info' : ''}" data-value="20">
                20
            </button>
            <button type="button" class="btn btn-default btn-sm btn-paging ${selectedValue === 50 ? 'btn-info' : ''}" data-value="50">
                50
            </button>
            <button type="button" class="btn btn-default btn-sm btn-paging ${selectedValue === 100 ? 'btn-info' : ''}" data-value="100">
                100
            </button>
			<button type="button" class="btn btn-default btn-sm btn-paging ${selectedValue === 500 ? 'btn-info' : ''}" data-value="500">
			    500 <!-- Corrected data-value to 500 -->
			</button>
            <button type="button" class="btn btn-default btn-sm btn-paging ${selectedValue === 'ALL' ? 'btn-info' : ''}" data-value="ALL">
                ALL
            </button>
        </div>
    </div>
 
`;
document.querySelector('.layout-main-section.frappe-card').appendChild(div);

// Add event listeners to pagination buttons
document.querySelectorAll('.btn-paging').forEach(button => {
    button.addEventListener('click', function() {
        var value = this.getAttribute('data-value');
        if (selectedValue === value) {
            return;
        } else {
            // Remove 'btn-info' class from all buttons
            document.querySelectorAll('.btn-paging').forEach(btn => {
                btn.classList.remove('btn-info');
            });
            // Add 'btn-info' class to the clicked button
            this.classList.add('btn-info');
            selectedValue = value;
            // Call execute function with the selected value
            execute(value);
        }
    });
});
