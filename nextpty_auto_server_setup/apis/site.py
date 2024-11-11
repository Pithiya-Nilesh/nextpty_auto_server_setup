import frappe, requests


@frappe.whitelist()
def create_site(docname):
    doc = frappe.get_doc("Customer Site Details", docname)
    for site in doc.site_details:
        if site.status == "Creation Pending":
            create_site_in_frappe_cloud(site.site_name)
       
            
            
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
    
    response = requests.post()