import json
from frappe.utils.password import get_decrypted_password
import frappe, requests


@frappe.whitelist()
def create_site_in_frappe_cloud(site_name):
    try:
        frappe_credentials = frappe.get_single("Frappe Cloud Credentials")
        
        url = f"{frappe_credentials.url}/api/method/press.api.site.new"
        
        headers = {
            "X-Press-Team": frappe_credentials.team,
            "Authorization": f"""token {frappe_credentials.api_key}:{get_decrypted_password("Frappe Cloud Credentials", "Frappe Cloud Credentials", "api_secret")}"""
        }
        
        data = {
            "site": {
                "name": site_name,
                "apps": get_apps(),
                "group": frappe_credentials.bench_id,
                "cluster": frappe_credentials.cluster,
                "plan": frappe_credentials.default_site_plan
            }
        }

        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            status = "Success"
            response = response.text
        else:
            status = "Failed"
            response = response.text
            
        set_frappe_cloud_logs(status, site_name, data, response, "Create New Site")
    except Exception as e:
        frappe.log_error("Error: While Creating New Site In Frappe Cloud", f"Error: {e}\nsite_name: {site_name}")


def get_apps():
    apps = []
    frappe_credentials = frappe.get_single("Frappe Cloud Credentials")
    for app in frappe_credentials.apps_to_install_in_site:
        apps.append(app.app_name.lower().replace(" ", "_").replace("-", "_"))
    return apps


@frappe.whitelist()
def activate_site(site_name):
    try:
        frappe_credentials = frappe.get_single("Frappe Cloud Credentials")
        
        url = f"{frappe_credentials.url}/api/method/press.api.site.activate"
        
        headers = {
            "X-Press-Team": frappe_credentials.team,
            "Authorization": f"""token {frappe_credentials.api_key}:{get_decrypted_password("Frappe Cloud Credentials", "Frappe Cloud Credentials", "api_secret")}"""
        }
        
        data =  {
            "name": f"{site_name}.frappe.cloud"
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            status = "Success"
            response = response.text
        else:
            status = "Failed"
            response = response.text
            
        set_frappe_cloud_logs(status, site_name, data, response, "Activate Site")
        
    except Exception as e:
        frappe.log_error("Error: While Activate Site In Frappe Cloud", f"Error: {e}\nsite_name: {site_name}")


@frappe.whitelist()
def deactivate_site(site_name):
    try:
        frappe_credentials = frappe.get_single("Frappe Cloud Credentials")
        
        url = f"{frappe_credentials.url}/api/method/press.api.site.deactivate"
        
        headers = {
            "X-Press-Team": frappe_credentials.team,
            "Authorization": f"""token {frappe_credentials.api_key}:{get_decrypted_password("Frappe Cloud Credentials", "Frappe Cloud Credentials", "api_secret")}"""
        }
        
        data = {
            "name": f"{site_name}.frappe.cloud"
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            status = "Success"
            response = response.text
        else:
            status = "Failed"
            response = response.text
            
        set_frappe_cloud_logs(status, site_name, data, response, "Deactivate Site")
        
    except Exception as e:
        frappe.log_error("Error: While Deactivate Site In Frappe Cloud", f"Error: {e}\nsite_name: {site_name}")



@frappe.whitelist()
def drop_site(site_name):
    try:
        frappe_credentials = frappe.get_single("Frappe Cloud Credentials")
        
        url = f"{frappe_credentials.url}/api/method/press.api.site.archive?force=0"
        
        headers = {
            "X-Press-Team": frappe_credentials.team,
            "Authorization": f"""token {frappe_credentials.api_key}:{get_decrypted_password("Frappe Cloud Credentials", "Frappe Cloud Credentials", "api_secret")}"""
        }
        
        data = {
            "name": f"{site_name}.frappe.cloud"
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            status = "Success"
            response = response.text
        else:
            status = "Failed"
            response = response.text
            
        set_frappe_cloud_logs(status, site_name, data, response, "Drop Site")
        
    except Exception as e:
        frappe.log_error("Error: While Deactivate Site In Frappe Cloud", f"Error: {e}\nsite_name: {site_name}")

        
        
@frappe.whitelist()
def update_site_status(row_name, status, action):
    site = frappe.db.sql(f""" SELECT status, site_name FROM `tabSite Details` WHERE name="{row_name}" """, as_dict=True)
    if site:
        if action == "activate":
            if site[0]['status'] == "Inactive":
                activate_site(site[0]['site_name'])

        if action == "deactivate":
            if site[0]['status'] == "Active":
                deactivate_site(site[0]['site_name'])
            
        if action == "drop":
            if site[0]['status'] == "Active":
                drop_site(site[0]['site_name'])
    

def set_frappe_cloud_logs(status, site_name, request, response, type_of_api):
    try:
        log = frappe.new_doc("Site Creation Log")
        log.status = status
        log.site = site_name
        log.request = json.dumps(request, indent=4)
        log.response = json.dumps(response, indent=4)
        log.type_of_api = type_of_api
        log.save()
    except Exception as e:
        frappe.log_error("Error: While Set FC API Log", f"site name: {site_name}\nstatus: {status}\nresponse: {response}\nError: {e}")
