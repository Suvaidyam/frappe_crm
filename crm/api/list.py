import frappe

@frappe.whitelist(allow_guest=True)
def get_list_views():
    return frappe.get_all('Frontend Views', fields=['name', 'label','document_type','icon'])

@frappe.whitelist(allow_guest=True)
def get_tabs(name):
    return frappe.get_all('Frontend Views Tab',filters={"parent":name} ,fields=['name', 'label','icon','doc_type'])