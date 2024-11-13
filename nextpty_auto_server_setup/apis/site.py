import frappe, requests


@frappe.whitelist()
def create_site_in_frappe_cloud(site_name):
    
    frappe_credentials = frappe.get_single("Frappe Cloud Credentials")
    
    url = f"{frappe_credentials.url}/api/method/press.api.site.new"
    
    headers = {
        "X-Press-Team": frappe_credentials.team,
        "Authorization": f"token {frappe_credentials.api_key}:{frappe_credentials.api_secret}"
    }
    
    data = {
        "site": {
            "name": site_name,
            "apps": [
                "frappe",
                "erpnext"
            ],
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
