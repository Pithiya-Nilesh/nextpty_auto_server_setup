from frappe.utils.password import get_decrypted_password
import frappe, requests


@frappe.whitelist()
def create_site_in_frappe_cloud(site_name):
    
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
        frappe.log_error("Site creation success")
    else:
        frappe.log_error("Site creation failed", response)
        frappe.log_error("Site creation failed text", response.text)

def get_apps():
    apps = []
    frappe_credentials = frappe.get_single("Frappe Cloud Credentials")
    for app in frappe_credentials.apps_to_install_in_site:
        apps.append(app.app_name.lower().replace(" ", "_").replace("-", "_"))
    return apps
