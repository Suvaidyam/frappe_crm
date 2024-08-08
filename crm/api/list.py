import frappe

@frappe.whitelist(allow_guest=True)
def get_list_views():
    return frappe.get_all('Frontend Views', fields=['name', 'label','document_type','icon','is_default'],order_by='is_default DESC, creation ASC')

@frappe.whitelist(allow_guest=True)
def get_default_page():
    return frappe.get_all('Frontend Views',filters={"is_default":1}, fields=['name', 'label','document_type','icon'],order_by='is_default DESC, creation ASC')

@frappe.whitelist(allow_guest=True)
def get_tabs(name):
    return frappe.get_all('Frontend Views Tab',filters={"parent":name} ,fields=['name', 'label','is_linked_document','linked_document','target_field','parent_document'],order_by='idx')