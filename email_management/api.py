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
	account.check_smtp_is_enabled()  # raises if not enabled
	from frappe.email.smtp import SMTPServer

	server = SMTPServer(
		login=account.login_id or account.email_id,
		password=account.get_password(),
		server=account.smtp_server,
		port=account.smtp_port,
		use_tls=account.use_tls,
		use_ssl=account.use_ssl_for_outgoing,
	)
	server.session  # triggers connection; raises on failure
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
	account.check_imap_is_enabled()  # raises if not enabled
	account.get_incoming_server()  # triggers connection; raises on failure
	return {"status": "ok"}
