import frappe
from frappe import _

from crm.api.doc import get_fields_meta, get_assigned_users
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script

@frappe.whitelist()
def get_doc(doctype,name):
	Doc = frappe.qb.DocType(doctype)

	query = frappe.qb.from_(Doc).select("*").where(Doc.name == name).limit(1)

	doc = query.run(as_dict=True)
	if not len(doc):
		frappe.throw(_("Doc not found"), frappe.DoesNotExistError)
	doc = doc.pop()

	doc["doctype"] = doctype
	doc["fields_meta"] = get_fields_meta(doctype)
	doc["_form_script"] = get_form_script(doctype)
	doc["_assign"] = get_assigned_users(doctype, doc.name, doc.owner)
	return doc

@frappe.whitelist()
def get_activities(name):
	if frappe.db.exists("CRM Deal", name):
		return get_deal_activities(name)
	elif frappe.db.exists("CRM Lead", name):
		return get_lead_activities(name)
	else:
		frappe.throw(_("Document not found"), frappe.DoesNotExistError)
@frappe.whitelist()
def get_fields_layout(doctype: str, type: str):
	sections = []
	if frappe.db.exists("CRM Fields Layout", {"dt": doctype, "type": type}):
		layout = frappe.get_doc("CRM Fields Layout", {"dt": doctype, "type": type})
	else:
		return []

	if layout.layout:
		sections = json.loads(layout.layout)

	allowed_fields = []
	for section in sections:
		if not section.get("fields"):
			continue
		allowed_fields.extend(section.get("fields"))

	fields = frappe.get_meta(doctype).fields
	fields = [field for field in fields if field.fieldname in allowed_fields]

	for section in sections:
		for field in section.get("fields") if section.get("fields") else []:
			field = next((f for f in fields if f.fieldname == field), None)
			if field:
				if field.fieldtype == "Select":
					field.options = field.options.split("\n")
					field.options = [{"label": _(option), "value": option} for option in field.options]
					field.options.insert(0, {"label": "", "value": ""})
				field = {
					"label": _(field.label),
					"name": field.fieldname,
					"type": field.fieldtype,
					"options": field.options,
					"mandatory": field.reqd,
				}
				section["fields"][section.get("fields").index(field["name"])] = field

	return sections or []