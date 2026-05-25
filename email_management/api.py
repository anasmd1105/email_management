import frappe
from frappe import _


@frappe.whitelist()
def test_outgoing_connection(company):
	mapping = frappe.db.get_value(
		"Company Email Account",
		{"company": company, "enabled": 1},
		"outgoing_email_account",
	)
	if not mapping:
		frappe.throw(_("No active Company Email Account found for {0}").format(company))

	account = frappe.get_doc("Email Account", mapping)
	account.validate_smtp_conn()
	return {"status": "ok"}


@frappe.whitelist()
def test_incoming_connection(company):
	mapping = frappe.db.get_value(
		"Company Email Account",
		{"company": company, "enabled": 1},
		"incoming_email_account",
	)
	if not mapping:
		frappe.throw(_("No active Company Email Account found for {0}").format(company))

	account = frappe.get_doc("Email Account", mapping)
	account.get_incoming_server()
	return {"status": "ok"}
