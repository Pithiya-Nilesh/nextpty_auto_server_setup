import frappe
from frappe.utils import get_abbr
import requests

SITE_STATUSES = ["Pending", "Installing", "Updating", "Active", "Inactive", "Broken", "Archived", "Suspended"]


def site_status_change(payload):
    # {'event': 'Site Status Update', 'data': {'doctype': 'Site', 'name': 'apisite.frappe.cloud', 'owner': 'rakesh@sanskartechnolab.com', 'creation': '2024-11-08 12:02:07.854563', 'modified': '2024-11-08 13:38:55.135773', 'modified_by': 'rakesh@sanskartechnolab.com', 'docstatus': 0, 'idx': 0, 'ip': None, 'status': 'Active', 'group': 'bench-16986', 'notify_email': 'roderick.guerra.g@gmail.com', 'team': '7138a70e2f', 'plan': 'Unlimited - Supported', 'setup_wizard_complete': 1, 'archive_failed': 0, 'cluster': 'Virginia', 'bench': 'bench-16986-000003-f41-virginia', 'is_database_access_enabled': 0, 'trial_end_date': None, 'tags': [], 'server': 'f41-virginia.frappe.cloud', 'host_name': 'apisite.frappe.cloud', 'skip_auto_updates': 0, 'additional_system_user_created': 0}}
    try:
        data = payload.get('data')
        site = data.get('name').split(".")[0]
        status = data.get('status')
        
        parent = frappe.db.sql(f""" SELECT parent FROM `tabSite` WHERE site_name="{site}" """, as_dict=True)
        if parent and status in SITE_STATUSES:
            doc = frappe.get_doc("Customer Site Details", parent[0]['parent'])
            for d_site in doc.site_details:
                if d_site.site_name == site:
                    d_site.status = status
            doc.save(ignore_permissions=True)
            frappe.db.commit()
        
        if status == "Active":
            auto_setup_site(site, parent[0]['parent'])
        
    except Exception as e:
        frappe.log_error("Error: While update site status using webhooks", f"Error: {e}\npayload: {payload}")
        return e


@frappe.whitelist()
def auto_setup_site(site, parent):
    site = f"{site}.frappe.cloud"
    company = frappe.db.get_value("Customer Site Details", parent, 'customer')
    data = frappe.db.sql(f""" SELECT site_owner_email, site_owner_name FROM `tabSite Details` WHERE site_name="{site}" and parent="{parent}" """, as_dict=True)
    if data:
        email = data[0]['site_owner_email']
        first_name = data[0]['site_owner_name']
    
        data = {
            "language": "Español (Colombia)",
            "country": "Panamá",
            "timezone": "America/Panama",
            "currency": "USD",
            
            "company_name": company,
            "company_abbr": get_abbr(company),
            
            "chart_of_accounts": "India - Chart of Accounts",
            "fy_start_date": "2024-04-01",
            "fy_end_date": "2025-03-31",
            "setup_demo": 0
        }
        
        url = f"https://{site}/api/method/nextpty_customization.apis.auto_setup.custom_setup_complete?args={data}&email={email}&first_name={first_name}"

        res = requests.post(url=url)
        print("\n\n res code", res.status_code)
        print("\n\n res text", res.text)
        frappe.log_error("Auto creaton", f"code: {res.status_code}\ntext: {res.text}")
