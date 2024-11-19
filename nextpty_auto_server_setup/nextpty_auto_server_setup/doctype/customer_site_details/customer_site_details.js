// Copyright (c) 2024, NextPTY and contributors
// For license information, please see license.txt

// frappe.ui.form.on("Customer Site Details", {
// 	refresh(frm) {

// 	},
// });


frappe.ui.form.on('Site Details', {
    activate: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.call({
            method: 'nextpty_auto_server_setup.apis.site.update_site_status',
            args: {
                row_name: row.name,
                status: row.status,
                action: "activate"
            },
            callback: function(res){
                console.log("res actvate", res.message)
            },
            freeze: true,
            freeze_message: "Please wait we are activating site."
        })
    },
    deactivate: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.call({
            method: 'nextpty_auto_server_setup.apis.site.update_site_status',
            args: {
                row_name: row.name,
                status: row.status,
                action: "deactivate"
            },
            callback: function(res){
                console.log("res deactivate", res.message)
            },
            freeze: true,
            freeze_message: "Please wait we are deactivating site."
        })
    },
    drop: function(frm, cdt, cdn) {
        let row = locals[cdt][cdn];
        frappe.call({
            method: 'nextpty_auto_server_setup.apis.site.update_site_status',
            args: {
                row_name: row.name,
                status: row.status,
                action: "drop"
            },
            callback: function(res){
                console.log("res drop", res.message)
            },
            freeze: true,
            freeze_message: "Please wait we are droping site."
        })
    },
});
