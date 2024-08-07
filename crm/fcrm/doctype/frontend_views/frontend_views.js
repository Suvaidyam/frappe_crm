// Copyright (c) 2024, Frappe Technologies Pvt. Ltd. and contributors
// For license information, please see license.txt

frappe.ui.form.on("Frontend Views", {
	refresh(frm) {

	},
});
let parent_options = [];
let linked_doc_options = [];
frappe.ui.form.on("Frontend Views Tab", {
    async form_render(frm, cdt, cdn) {
        let connection_fields = await frappe.call('crm.api.get_doc.get_link_fields', {doctype: frm.doc.document_type,connections:true});
        parent_options = connection_fields.message?.map((field) => {return {label:field.link_doctype, value:field.link_doctype,description:field.link_fieldname}});
        let fields = await frappe.call('crm.api.get_doc.get_link_fields', {doctype: frm.doc.document_type});
        linked_doc_options = fields.message?.map((field) => {return {label:field.options, value:field.options,description:field.fieldname}});
        frm.cur_grid.grid_form.fields_dict.linked_document.set_data(linked_doc_options);
        frm.cur_grid.grid_form.fields_dict.parent_document.set_data(parent_options);
    },
    async linked_document(frm, cdt, cdn) {
        let doc = locals[cdt][cdn];
        if(doc.linked_document){
            let target = linked_doc_options.find((option) => option.value === doc.linked_document);
            doc.target_field = target.description;
            frm.cur_grid.refresh();
        }
    },
    async parent_document(frm, cdt, cdn) {
        let doc = locals[cdt][cdn];
        if(doc.parent_document){
            let target = parent_options.find((option) => option.value === doc.parent_document);
            doc.target_field = target.description;
            frm.cur_grid.refresh();
        }
    },
    async is_linked_document(frm, cdt, cdn) {
        let doc = locals[cdt][cdn];
        if(doc.is_linked_document){
            doc.parent_document = "";
        }else{
            doc.linked_document = "";
        }
        doc.target_field = "";
        frm.cur_grid.refresh();
    }
})
