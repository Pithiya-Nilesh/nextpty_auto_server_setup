import frappe, json

from nextpty_auto_server_setup.apis.site import check_site_status


@frappe.whitelist()
def check_new_site_status():
    sql = f""" 
        SELECT parent, site_name FROM `tabSite Details` WHERE is_new_site=1
    """
    sites_details = frappe.db.sql(sql, as_dict=True)
    if sites_details:
        for site in sites_details:
            site_status = check_site_status(site['site_name'])
            if site_status == "Active":
                frappe.enqueue("nextpty_auto_server_setup.webhooks.site_status_change.configure_site_for_active_status", site=site['site_name'], parent=site['parent'], timeout=1000)