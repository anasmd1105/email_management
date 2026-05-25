import frappe


SUPPLIER_DOCTYPES = [
	("Purchase Order", "supplier_address", "supplier_email"),
	("Purchase Receipt", "supplier_address", "supplier_email"),
	("Supplier Quotation", "supplier_address", "supplier_email"),
	("Subcontracting Order", "supplier_address", "supplier_email"),
	("Subcontracting Receipt", "supplier_address", "supplier_email"),
]

CUSTOMER_DOCTYPES = [
	("Sales Invoice", "customer_address", "customer_email"),
	("Sales Order", "customer_address", "customer_email"),
	("Quotation", "customer_address", "customer_email"),
	("Delivery Note", "customer_address", "customer_email"),
]


def execute():
	for doctype, fetch_from_field, fieldname in SUPPLIER_DOCTYPES + CUSTOMER_DOCTYPES:
		_add_field(doctype, fetch_from_field, fieldname)
	_add_user_company_field()


def _add_field(doctype, fetch_from_field, fieldname):
	custom_field_name = f"{doctype}-{fieldname}"

	if frappe.db.exists("Custom Field", custom_field_name):
		return

	# Skip if the doctype doesn't exist in this installation
	if not frappe.db.exists("DocType", doctype):
		return

	try:
		frappe.get_doc(
			{
				"doctype": "Custom Field",
				"dt": doctype,
				"fieldname": fieldname,
				"label": "Supplier Email" if "supplier" in fieldname else "Customer Email",
				"fieldtype": "Data",
				"options": "Email",
				"fetch_from": f"{fetch_from_field}.email_id",
				"fetch_if_empty": 1,
				"hidden": 1,
				"insert_after": "contact_email" if frappe.get_meta(doctype).get_field("contact_email") else "",
			}
		).insert(ignore_permissions=True)
	except Exception:
		pass


def _add_user_company_field():
	if frappe.db.exists("Custom Field", "User-company"):
		return

	try:
		frappe.get_doc(
			{
				"doctype": "Custom Field",
				"dt": "User",
				"fieldname": "company",
				"label": "Company",
				"fieldtype": "Link",
				"options": "Company",
				"insert_after": "full_name",
			}
		).insert(ignore_permissions=True)
	except Exception:
		pass
