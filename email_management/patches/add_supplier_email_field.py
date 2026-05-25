import frappe


def execute():
	if frappe.db.exists("Custom Field", "Purchase Invoice-supplier_email"):
		return

	frappe.get_doc(
		{
			"doctype": "Custom Field",
			"dt": "Purchase Invoice",
			"fieldname": "supplier_email",
			"label": "Supplier Email",
			"fieldtype": "Data",
			"options": "Email",
			"fetch_from": "supplier_address.email_id",
			"fetch_if_empty": 1,
			"hidden": 1,
			"insert_after": "contact_email",
		}
	).insert(ignore_permissions=True)
