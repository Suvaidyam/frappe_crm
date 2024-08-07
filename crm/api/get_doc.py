import frappe
from frappe import _
from crm.api.doc import get_fields_meta, get_assigned_users
from crm.fcrm.doctype.crm_form_script.crm_form_script import get_form_script
from frappe.utils.caching import redis_cache
from frappe.desk.form.load import get_docinfo
import json

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
def get_activities(doctype, name):
    if frappe.db.exists(doctype, name):
        get_docinfo('', doctype, name)
        docinfo = frappe.response["docinfo"]
        doc_meta = frappe.get_meta(doctype)
        doc_fields = {field.fieldname: {"label": field.label, "options": field.options} for field in doc_meta.fields}
        doc = frappe.db.get_value(doctype, name, ["creation", "owner"])
        activities = [{
            "activity_type": "creation",
            "creation": doc[0],
            "owner": doc[1],
            "data": "created this item",
            "is_lead": False
        }]
        
        docinfo.versions.reverse()
        for version in docinfo.versions:
            data = json.loads(version.data)
            if not data.get("changed"):
                continue

            change = data.get("changed")[0]
            if not change:
                continue

            field = doc_fields.get(change[0])
            if not field or (not change[1] and not change[2]):
                continue

            field_label = field.get("label") or change[0]
            field_option = field.get("options")

            activity_type = "changed"
            data = {
                "field": change[0],
                "field_label": field_label,
                "old_value": change[1],
                "value": change[2],
            }

            if not change[1] and change[2]:
                activity_type = "added"
                data = {
                    "field": change[0],
                    "field_label": field_label,
                    "value": change[2],
                }
            elif change[1] and not change[2]:
                activity_type = "removed"
                data = {
                    "field": change[0],
                    "field_label": field_label,
                    "value": change[1],
                }

            activity = {
                "activity_type": activity_type,
                "creation": version.creation,
                "owner": version.owner,
                "data": data,
                "is_lead": True,
                "options": field_option,
            }
            activities.append(activity)

        # Handle comments
        for comment in docinfo.comments:
            activity = {
                "name": comment.name,
                "activity_type": "comment",
                "creation": comment.creation,
                "owner": comment.owner,
                "content": comment.content,
                "attachments": get_attachments('Comment', comment.name),
                "is_lead": True,
            }
            activities.append(activity)

        # Handle communications
        for communication in docinfo.communications + docinfo.automated_messages:
            activity = {
                "activity_type": "communication",
                "communication_type": communication.communication_type,
                "creation": communication.creation,
                "data": {
                    "subject": communication.subject,
                    "content": communication.content,
                    "sender_full_name": communication.sender_full_name,
                    "sender": communication.sender,
                    "recipients": communication.recipients,
                    "cc": communication.cc,
                    "bcc": communication.bcc,
                    "attachments": get_attachments('Communication', communication.name),
                    "read_by_recipient": communication.read_by_recipient,
                },
                "is_lead": True,
            }
            activities.append(activity)

        notes = get_linked_notes(doctype,name)
        tasks = get_linked_tasks(doctype,name)
        
        activities.sort(key=lambda x: x["creation"], reverse=True)
        return activities,[], notes, tasks
    else:
        frappe.throw(_("Activities not found"), frappe.DoesNotExistError)

@redis_cache()
def get_attachments(doctype, name):
	return frappe.db.get_all(
		"File",
		filters={"attached_to_doctype": doctype, "attached_to_name": name},
		fields=["name", "file_name", "file_url", "file_size", "is_private"],
	)

def get_linked_notes(doctype,name):
	notes = frappe.db.get_all(
		"FCRM Note",
		filters={"reference_doctype":doctype,"reference_docname": name},
		fields=['name', 'title', 'content', 'owner', 'modified'],
	)
	return notes or []

def get_linked_tasks(doctype,name):
	tasks = frappe.db.get_all(
		"CRM Task",
		filters={"reference_doctype":doctype,"reference_docname": name},
		fields=[
			"name",
			"title",
			"description",
			"assigned_to",
			"assigned_to",
			"due_date",
			"priority",
			"status",
			"modified",
		],
	)
	return tasks or []

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



@frappe.whitelist()
def get_fields_meta(doctype, restricted_fieldtypes=None, as_array=False):
	not_allowed_fieldtypes = [
		"Tab Break",
		"Section Break",
		"Column Break",
	]
	if restricted_fieldtypes:
		restricted_fieldtypes = frappe.parse_json(restricted_fieldtypes)
		not_allowed_fieldtypes += restricted_fieldtypes

	fields = frappe.get_meta(doctype).fields
	fields = [field for field in fields if field.fieldtype not in not_allowed_fieldtypes]

	# standard_fields = [
	# 	{"fieldname": "name", "fieldtype": "Link", "label": "ID", "options": doctype},
	# 	{
	# 		"fieldname": "owner",
	# 		"fieldtype": "Link",
	# 		"label": "Created By",
	# 		"options": "User"
	# 	},
	# 	{
	# 		"fieldname": "modified_by",
	# 		"fieldtype": "Link",
	# 		"label": "Last Updated By",
	# 		"options": "User",
	# 	},
	# 	{"fieldname": "_user_tags", "fieldtype": "Data", "label": "Tags"},
	# 	{"fieldname": "_liked_by", "fieldtype": "Data", "label": "Like"},
	# 	{"fieldname": "_comments", "fieldtype": "Text", "label": "Comments"},
	# 	{"fieldname": "_assign", "fieldtype": "Text", "label": "Assigned To"},
	# 	{"fieldname": "creation", "fieldtype": "Datetime", "label": "Created On"},
	# 	{"fieldname": "modified", "fieldtype": "Datetime", "label": "Last Updated On"},
	# ]

	# for field in standard_fields:
	# 	if not restricted_fieldtypes or field.get('fieldtype') not in restricted_fieldtypes:
	# 		fields.append(field)

	if as_array:
		return fields
	fields_meta = {}
	for field in fields:
		fields_meta[field.get('fieldname')] = field
	return fields_meta

@frappe.whitelist()
def get_link_fields(doctype,connections=False):
    if connections:
        return frappe.get_meta(doctype).links
    else:
        fields = [field for field in frappe.get_meta(doctype).fields if field.fieldtype  == 'Link']
        return fields