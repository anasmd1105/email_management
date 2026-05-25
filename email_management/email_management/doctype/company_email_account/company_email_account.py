import frappe
from frappe.model.document import Document


class CompanyEmailAccount(Document):
	def validate(self):
		self.validate_unique_active_company()
		self.validate_outgoing_account()
		self.validate_incoming_account()

	def on_update(self):
		self.clear_email_account_cache()

	def validate_unique_active_company(self):
		if not self.enabled:
			return
		existing = frappe.db.get_value(
			"Company Email Account",
			{
				"company": self.company,
				"enabled": 1,
				"name": ("!=", self.name),
			},
			"name",
		)
		if existing:
			frappe.throw(
				frappe._("An active Company Email Account already exists for {0}: {1}").format(
					self.company, existing
				)
			)

	def validate_outgoing_account(self):
		if not self.outgoing_email_account:
			return
		enable_outgoing = frappe.db.get_value(
			"Email Account", self.outgoing_email_account, "enable_outgoing"
		)
		if not enable_outgoing:
			frappe.throw(
				frappe._("Email Account {0} does not have outgoing (SMTP) enabled.").format(
					self.outgoing_email_account
				)
			)

	def validate_incoming_account(self):
		if not self.incoming_email_account:
			return
		enable_incoming = frappe.db.get_value(
			"Email Account", self.incoming_email_account, "enable_incoming"
		)
		if not enable_incoming:
			frappe.throw(
				frappe._("Email Account {0} does not have incoming (IMAP/POP) enabled.").format(
					self.incoming_email_account
				)
			)

	def clear_email_account_cache(self):
		for key in (
			"outgoing_email_account",
			"incoming_email_account",
			"default_outgoing",
			"default_incoming",
		):
			frappe.cache().delete_key(key)
