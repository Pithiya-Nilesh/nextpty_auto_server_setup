import json
import frappe
from frappe.utils import get_abbr
from nextpty_auto_server_setup.apis.site_domain import create_dns_record_and_add_domain
import requests

SITE_STATUSES = ["Pending", "Installing", "Updating", "Active", "Inactive", "Broken", "Archived", "Suspended"]


def site_status_change(payload):
    # {'event': 'Site Status Update', 'data': {'doctype': 'Site', 'name': 'apisite.frappe.cloud', 'owner': 'rakesh@sanskartechnolab.com', 'creation': '2024-11-08 12:02:07.854563', 'modified': '2024-11-08 13:38:55.135773', 'modified_by': 'rakesh@sanskartechnolab.com', 'docstatus': 0, 'idx': 0, 'ip': None, 'status': 'Active', 'group': 'bench-16986', 'notify_email': 'roderick.guerra.g@gmail.com', 'team': '7138a70e2f', 'plan': 'Unlimited - Supported', 'setup_wizard_complete': 1, 'archive_failed': 0, 'cluster': 'Virginia', 'bench': 'bench-16986-000003-f41-virginia', 'is_database_access_enabled': 0, 'trial_end_date': None, 'tags': [], 'server': 'f41-virginia.frappe.cloud', 'host_name': 'apisite.frappe.cloud', 'skip_auto_updates': 0, 'additional_system_user_created': 0}}
    try:
        data = payload.get('data')
        site = data.get('name').split(".")[0]
        status = data.get('status')
        
        parent = frappe.db.sql(f""" SELECT parent FROM `tabSite Details` WHERE site_name="{site}" """, as_dict=True)
        if parent and status in SITE_STATUSES:
            doc = frappe.get_doc("Customer Site Details", parent[0]['parent'])
            for d_site in doc.site_details:
                if d_site.site_name == site:
                    d_site.status = status
            doc.save(ignore_permissions=True)
            frappe.db.commit()
        
        if status == "Active" and parent:
            configure_site_for_active_status(site, parent[0]['parent'])
        
    except Exception as e:
        frappe.log_error("Error: While update site status using webhooks", f"Error: {e}\npayload: {payload}")
        return e


@frappe.whitelist()
def configure_site_for_active_status(site, parent):
    try:
        site_name = f"{site}.frappe.cloud"
        company = frappe.db.get_value("Customer Site Details", parent, 'customer')
        data = frappe.db.sql(f""" SELECT name, is_new_site, site_owner_email, site_owner_name FROM `tabSite Details` WHERE site_name="{site}" and parent="{parent}" """, as_dict=True)
        if data:
            if data[0]['is_new_site']:
                        
                email = data[0]['site_owner_email']
                first_name = data[0]['site_owner_name']
                from datetime import datetime
                today = datetime.now()
                fy_start_date = f"{today.year}-01-01"
                fy_end_date = f"{today.year}-12-31"
                args = {
                    "language": "Español (Colombia)",
                    "country": "Panamá",
                    "timezone": "America/Panama",
                    "currency": "USD",
                    "company_name": company,
                    "company_abbr": get_abbr(company),
                    "chart_of_accounts": "Standard with Numbers",
                    "fy_start_date": f"{fy_start_date}",
                    "fy_end_date": f"{fy_end_date}",
                    "setup_demo": 0
                }
                
                url = f"https://{site_name}/api/method/nextpty_customization.apis.auto_setup.custom_setup_complete?args={json.dumps(args)}&email={email}&first_name={first_name}"
                res = requests.post(url=url)
                frappe.log_error("Auto creation", f"code: {res.status_code}\ntext: {res.text}")
                
                frappe.db.sql(f""" UPDATE `tabSite Details` SET is_new_site=0 WHERE name="{data[0]['name']}" """)
                frappe.db.commit()
                
                res = json.loads(res.text)
                if res['message'].get('status') != "already setup":
                    create_dns_record_and_add_domain(site, parent)
                    send_site_active_email(site, parent, res)

    except Exception as e:
        frappe.log_error("Error: While auto setup new site", f"Error: {e}\nsite: {site}\nparent: {parent}")


@frappe.whitelist()
def send_site_active_email(site, parent, res):
    """ add email configuration to send email after site active """
    try:
        site_name = f"{site}.nextpty.com"
        # res = {'message': {'user': 'nilesh@sanskartechnolab.com', 'password': 'ezI6UDmKPb', 'site': 'https://johntradinginc.frappe.cloud'}, 'site': 'https://johntradinginc.nextpty.com'}
        # res = json.loads(res)
        res['message']['site'] = f"https://{site_name}"
        
        msg = res['message']
        
        # email_subject = "Welcome! Your Website is Live - Access Details Inside"
        email_subject = f"Tu sitio de trabajo {site_name} ha sido creado"
        
        email_template = f"""
            <h3>Tu sitio de trabajo {site_name} ha sido creado. Abajo los detalles para acceder:</h3><br>

            <p>URL: {msg['site']} </p>
            <p>Usuario: {msg['user']}  </p>
            <p>Password: {msg['password']}  </p><br>

            <p>Gracias por elegir NextPTY y darnos la oportunidad de demostrarte porqué ERP Next localizado por nosotros es la mejor opción para tu negocio.</p><br>
            <p>Cualquier duda que tengas, puedes contactarnos a soporte@nextpty.com</p><br>
            <p>Atentamente,</p>
            <p>NextPTY</p>
        """
        
        frappe.sendmail(recipients=[f"{msg['user']}"], sender="soporte@nextpty.com", subject=email_subject, message=email_template, now=True)
        frappe.log_error("Email send", f"site: {site_name}\nparent: {parent}\nres: {res}")
    except Exception as e:
        frappe.log_error("Error: While sending site creation email", f"Error: {e}\nparent: {parent}\nres: {res}")
