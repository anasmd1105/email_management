import frappe
from frappe import _
from frappe.core.doctype.user.user import User


class MultiCompanyUser(User):
	def send_welcome_mail_to_user(self):
		from frappe.utils import get_url
		from frappe.core.doctype.user.user import User as _BaseUser

		# Call reset_password via the base class to avoid any MRO attribute-lookup issue
		link = _BaseUser.reset_password(self)

		# Company on the user form takes priority over the global welcome_email hook
		# (ERPNext's hook always returns get_default_company(), ignoring the user's company)
		company_name = getattr(self, "company", None)
		if company_name:
			subject = _("Welcome to {0}").format(company_name)
		else:
			subject = None
			method = frappe.get_hooks("welcome_email")
			if method:
				subject = frappe.get_attr(method[-1])()
			if not subject:
				site_name = frappe.db.get_default("site_name") or frappe.get_conf().get("site_name")
				subject = _("Welcome to {0}").format(site_name) if site_name else _("Complete Registration")

		welcome_email_template = frappe.db.get_system_setting("welcome_email_template")

		self.send_login_mail(
			subject,
			"new_user",
			dict(
				link=link,
				site_url=get_url(),
			),
			custom_template=welcome_email_template,
		)

	def send_login_mail(self, subject, template, add_args, now=None, custom_template=None):
		"""Override to route welcome/login emails via the company's outgoing email account."""
		from frappe.utils import get_url, get_formatted_email
		from frappe.utils.user import get_user_fullname
		from frappe import STANDARD_USERS

		created_by = get_user_fullname(frappe.session["user"])
		if created_by == "Guest":
			created_by = "Administrator"

		args = {
			"first_name": self.first_name or self.last_name or "user",
			"user": self.name,
			"title": subject,
			"login_url": get_url(),
			"created_by": created_by,
		}

		args.update(add_args)

		sender = (
			frappe.session.user not in STANDARD_USERS and get_formatted_email(frappe.session.user)
		) or None

		content = None
		if custom_template:
			from frappe.email.doctype.email_template.email_template import get_email_template

			email_template = get_email_template(custom_template, args)
			subject = email_template.get("subject")
			content = email_template.get("message")

		frappe.sendmail(
			recipients=self.email,
			sender=sender,
			subject=subject,
			template=template if not custom_template else None,
			content=content if custom_template else None,
			args=args,
			header=[subject, "green"],
			delayed=(not now) if now is not None else self.flags.delay_emails,
			retry=3,
			reference_doctype="User",
			reference_name=self.name,
		)
