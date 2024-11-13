import frappe

SITE_STATUSES = ["Pending", "Installing", "Updating", "Active", "Inactive", "Broken", "Archived", "Suspended"]


def site_status_change(payload):
    # {'event': 'Site Status Update', 'data': {'doctype': 'Site', 'name': 'apisite.frappe.cloud', 'owner': 'rakesh@sanskartechnolab.com', 'creation': '2024-11-08 12:02:07.854563', 'modified': '2024-11-08 13:38:55.135773', 'modified_by': 'rakesh@sanskartechnolab.com', 'docstatus': 0, 'idx': 0, 'ip': None, 'status': 'Active', 'group': 'bench-16986', 'notify_email': 'roderick.guerra.g@gmail.com', 'team': '7138a70e2f', 'plan': 'Unlimited - Supported', 'setup_wizard_complete': 1, 'archive_failed': 0, 'cluster': 'Virginia', 'bench': 'bench-16986-000003-f41-virginia', 'is_database_access_enabled': 0, 'trial_end_date': None, 'tags': [], 'server': 'f41-virginia.frappe.cloud', 'host_name': 'apisite.frappe.cloud', 'skip_auto_updates': 0, 'additional_system_user_created': 0}}
    try:
        data = payload.get('data')
        site = data.get('site')
        status = data.get('status')
        
        parent = frappe.db.sql(f""" SELECT parent FROM `tabSite` WHERE site_name="{site}" """, as_dict=True)
        if parent and status in SITE_STATUSES:
            doc = frappe.get_doc("Customer Site Details", parent['parent'])
            for site in doc.site_details:
                if site.sit_name == site.split(".")[0]:
                    site.status = status
            doc.db_update()
            frappe.db.commit()
    except Exception as e:
        frappe.log_error("Error: While update site status using webhooks", f"Error: {e}\npayload: {payload}")
        return e
