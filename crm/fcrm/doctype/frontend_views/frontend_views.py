# Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class FrontendViews(Document):
	def before_insert(self):
		side_form = frappe.new_doc('CRM Fields Layout')
		side_form.update({
			'type': "Side Panel",
			'dt': self.document_type
		})
		side_form.insert(ignore_permissions=True)
		self.side_form_layout_link = side_form.name

	def on_update(self):
		exist = frappe.db.exists('CRM Fields Layout', {'type':"Side Panel",'dt':self.document_type})
		if exist:
			side_form = frappe.get_doc('CRM Fields Layout',exist)
			side_form.dt = self.document_type
			side_form.save()
		else:
			side_form = frappe.new_doc('CRM Fields Layout')
			side_form.update({
				'type': "Side Panel",
				'dt': self.document_type
			})
			side_form.insert(ignore_permissions=True)
			self.side_form_layout_link = side_form.name

	def on_trash(self):
		exist_side = frappe.db.exists('CRM Fields Layout', {'type':"Side Panel",'dt':self.side_form_layout_link})
		if exist_side:
			frappe.delete_doc('CRM Fields Layout',exist_side)
		pass
