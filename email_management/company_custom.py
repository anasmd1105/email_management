import frappe
from frappe.custom.doctype.custom_field.custom_field import create_custom_field

def create_custom_fields():
    custom_fields = {
        "Company": [
            {
                "fieldname": "company",
                "fieldtype": "Link",
                "label": "Company",
                "insert_after": "send_welcome_email",
                "in_list_view": 1,
                "in_filter":1,
                "reqd": 1,
                "options":"Company"
            }
    for doctype, fields in custom_fields.items():
        for field in fields:
            if not frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": field["fieldname"]}):
                create_custom_field(doctype, field)
                
                frappe.db.commit()
                frappe.clear_cache(doctype=doctype)


def delete_custom_fields():
    custom_fields_to_delete = {
        "Company": ["company"]
        
    }

    for doctype, fields in custom_fields_to_delete.items():
        for field_name in fields:
            if frappe.db.exists("Custom Field", {"dt": doctype, "fieldname": field_name}):
                frappe.delete_doc("Custom Field", f"{doctype}-{field_name}", ignore_missing=True)
                frappe.db.commit()
                frappe.clear_cache(doctype=doctype)
