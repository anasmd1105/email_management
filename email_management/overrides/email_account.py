import frappe
from frappe.email.doctype.email_account.email_account import EmailAccount


class MultiCompanyEmailAccount(EmailAccount):
	@classmethod
	def find_outgoing(cls, match_by_email=None, match_by_doctype=None, _raise_error=False):
		company = getattr(frappe.local, "_email_company_context", None)

		if company:
			account = cls._find_by_company(company, outgoing=True)
			if account:
				return account

		return super().find_outgoing(
			match_by_email=match_by_email,
			match_by_doctype=match_by_doctype,
			_raise_error=_raise_error,
		)

	@classmethod
	def find_incoming(cls, match_by_email=None, match_by_doctype=None):
		company = getattr(frappe.local, "_email_company_context", None)

		if company:
			account = cls._find_by_company(company, outgoing=False)
			if account:
				return account

		return super().find_incoming(
			match_by_email=match_by_email,
			match_by_doctype=match_by_doctype,
		)

	@classmethod
	def _find_by_company(cls, company, outgoing=True):
		mapping = frappe.db.get_value(
			"Company Email Account",
			{"company": company, "enabled": 1},
			[
				"outgoing_email_account",
				"incoming_email_account",
				"fallback_to_global_default",
			],
			as_dict=True,
		)

		if not mapping:
			return None

		account_name = mapping.outgoing_email_account if outgoing else mapping.incoming_email_account

		if account_name:
			return frappe.get_doc("Email Account", account_name)

		if not mapping.fallback_to_global_default:
			direction = "outgoing" if outgoing else "incoming"
			frappe.throw(
				frappe._("No {0} email account configured for company {1}.").format(
					direction, company
				)
			)

		return None
