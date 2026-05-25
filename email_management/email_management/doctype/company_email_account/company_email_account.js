frappe.ui.form.on("Company Email Account", {
	refresh(frm) {
		frm.set_query("outgoing_email_account", () => ({
			filters: { enable_outgoing: 1 },
		}));

		frm.set_query("incoming_email_account", () => ({
			filters: { enable_incoming: 1 },
		}));

		if (!frm.is_new()) {
			frm.add_custom_button(__("Test Outgoing"), () => {
				frappe.call({
					method: "email_management.api.test_outgoing_connection",
					args: { company: frm.doc.company },
					callback(r) {
						if (!r.exc) frappe.msgprint(__("Outgoing connection successful."));
					},
				});
			});

			frm.add_custom_button(__("Test Incoming"), () => {
				frappe.call({
					method: "email_management.api.test_incoming_connection",
					args: { company: frm.doc.company },
					callback(r) {
						if (!r.exc) frappe.msgprint(__("Incoming connection successful."));
					},
				});
			});
		}
	},
});
