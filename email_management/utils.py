import frappe

_email_queue_builder_patched = False


def apply_email_patches():
	"""
	Patch EmailQueueBuilder.get_outgoing_email_account once per worker process.
	This is called via before_request hook and patches at the builder level —
	which has direct access to reference_doctype and reference_name, so no
	frappe.local context is needed.
	"""
	global _email_queue_builder_patched
	if _email_queue_builder_patched:
		return

	try:
		from frappe.email.doctype.email_queue.email_queue import QueueBuilder

		_original_get_outgoing = QueueBuilder.get_outgoing_email_account

		def patched_get_outgoing_email_account(self):
			if self._email_account:
				return self._email_account

			# Try company-specific account using the reference document
			if self.reference_doctype and self.reference_name:
				company = _get_company_from_reference(self.reference_doctype, self.reference_name)
				if company:
					account = _find_by_company(company, outgoing=True)
					if account:
						self._email_account = account
						return self._email_account

			# Fall back to standard Frappe logic (uses default outgoing account)
			return _original_get_outgoing(self)

		QueueBuilder.get_outgoing_email_account = patched_get_outgoing_email_account
		_email_queue_builder_patched = True

	except Exception:
		pass


def _get_company_from_reference(doctype, docname):
	"""Return company from a reference document if it has a company field."""
	try:
		if not frappe.get_meta(doctype).get_field("company"):
			return None
		return frappe.db.get_value(doctype, docname, "company")
	except Exception:
		return None


def _find_by_company(company, outgoing=True):
	"""Look up Company Email Account mapping and return the configured Email Account doc."""
	mapping = frappe.db.get_value(
		"Company Email Account",
		{"company": company, "enabled": 1},
		["outgoing_email_account", "incoming_email_account", "fallback_to_global_default"],
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
			frappe._("No {0} email account configured for company {1}.").format(direction, company)
		)

	return None


def tag_communication_company(doc, method=None):
	"""Tag incoming Communications with the company that owns the receiving Email Account."""
	if doc.sent_or_received != "Received" or not doc.email_account:
		return

	company = frappe.db.get_value(
		"Company Email Account",
		{"incoming_email_account": doc.email_account, "enabled": 1},
		"company",
	)
	if company:
		frappe.db.set_value("Communication", doc.name, "company", company, update_modified=False)
