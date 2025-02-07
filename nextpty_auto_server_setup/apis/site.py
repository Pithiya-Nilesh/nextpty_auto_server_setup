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
        status = check_site_status(site_name)
        if status == "Inactive" or status == "Broken":
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
            return True if status == "Success" else False
        else:
            return True
        
    except Exception as e:
        frappe.log_error("Error: While Activate Site In Frappe Cloud", f"Error: {e}\nsite_name: {site_name}")


@frappe.whitelist()
def deactivate_site(site_name):
    try:
        status = check_site_status(site_name)
        if status == "Active" or status == "Broken":
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
            return True if status == "Success" else False
        else:
            return True
        
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
def check_site_status(site): 
    response = "" 
    try:
        frappe_credentials = frappe.get_single("Frappe Cloud Credentials")
        
        url = f"{frappe_credentials.url}/api/method/press.api.site.get"
        
        headers = {
            "X-Press-Team": frappe_credentials.team,
            "Authorization": f"""token {frappe_credentials.api_key}:{get_decrypted_password("Frappe Cloud Credentials", "Frappe Cloud Credentials", "api_secret")}"""
        }
        
        data = {
            "name": f"{site}.frappe.cloud"
        }

        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            response = json.loads(response.text)
            return response['message']['status']
        else:
            response = response.text
                    
    except Exception as e:
        frappe.log_error("Error: While Check Site Status In Frappe Cloud", f"Error: {e}\nsite_name: {site}\nresponse: {response}")
        
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
        frappe.db.commit()
    except Exception as e:
        frappe.log_error("Error: While Set FC API Log", f"site name: {site_name}\nstatus: {status}\nrequest: {request}\ntype_of_api: {type_of_api}\nresponse: {response}\nError: {e}")


@frappe.whitelist(allow_guest=True)
def get_site_data():
    try:
        session_user = frappe.session.user
        if session_user=="Guest":
            return {"redirect": "/login"}

        customers = frappe.get_all("Portal User",filters={"user":session_user,"parenttype":"Customer"},fields=["parent"])

        session_user_sites_details = []
        for customer in customers:
            customer_name = customer["parent"]
            customer_site_details = frappe.get_all("Customer Site Details",filters={"customer":customer_name},fields=["name"])
            for site_detail in customer_site_details:
                session_user_sites_details.append(site_detail["name"])

        site_info = [] 

        for session_user_site in session_user_sites_details:
            site_details = frappe.get_all("Site Details",filters={"parent":session_user_site,"parenttype":"Customer Site Details"},fields=["site_name","status"])

            for site in site_details:
                site_name = site["site_name"]
                status = site["status"]

                site_data = frappe.get_all("Site Subscription",filters={"parent":site_name,"parenttype":"Site"},fields=["subscription","is_active","is_trial","creation"])
                
                subscription = None  
                subscription_end_date = None
                is_trial = 0
                subscription_name = ""

                for subscription_data in site_data:
                    if subscription_data["is_active"] == 1:
                        subscription = "Active"

                        subscription_record = frappe.db.get_value("Subscription", subscription_data["subscription"], ["trial_period_end", "end_date", "name"], as_dict=True)
                        if subscription_record:
                            if subscription_data["is_trial"]==1:
                                subscription_end_date = subscription_record["trial_period_end"]
                                is_trial = 1
                            else:
                                subscription_end_date = subscription_record["end_date"]
                            subscription_name = subscription_record["name"]
                        break
                if not subscription:
                    subscription = "Expired"
                    if site_data:
                        last_subscription_data = sorted(site_data, key=lambda x: x["creation"], reverse=True)[0]

                        subscription_record = frappe.db.get_value(
                                    "Subscription",
                                    last_subscription_data["subscription"],
                                    ["end_date","trial_period_end", "name"],
                                    as_dict=True
                                )       
                        if subscription_record:             
                            if subscription_data["is_trial"]==1:
                                is_trial = 1
                                subscription_end_date = subscription_record["trial_period_end"]
                            else:
                                subscription_end_date = subscription_record["end_date"]
                            subscription_name = subscription_record["name"]
                site_info.append({
                    "site_name": site_name,
                    "status": status,
                    "subscription": get_subscription_status(subscription_name, site_name) if subscription == "Active" else subscription,
                    "is_trial": is_trial,
                    "save_card": get_save_card(session_user, site_name, 'card_number'),
                    "save_card_id": get_save_card(session_user, site_name, 'name'),
                    "expiry_date": get_subscription_end_date(subscription_end_date, site_name) if subscription_end_date else "",
                    "subscription_name": subscription_name,
                    "plan": "Trial" if is_trial else get_plan(subscription_name, site_name) if subscription_end_date else ""
                })
        return site_info
    except Exception as e:
        pass
        
    
def get_save_card(session_user, site_name, field):
    return frappe.db.get_value("Croem Saved Card Token", filters={"user": session_user, "site_name": site_name}, fieldname=[field])

def get_subscription_status(subscription, site_name):
    status = frappe.db.get_value("Subscription", subscription, fieldname=['status'])
    if frappe.db.get_value("Site", site_name, ['is_renew']):
        # return "Active"
        parent_doc = frappe.get_doc("Site", site_name)
        data = [row for row in parent_doc.get("site_subscription") if row.is_renew == 1][0]
        if frappe.db.get_value("Subscription", data.subscription, ['custom_is_cancelled']):
            return "Expired"
        else:
            return "Active"
    
    if status == "Past Due Date" or status == "Unpaid":
        return "Expired"
    else:
        return status

def get_subscription_end_date(date, site_name):
    if frappe.db.get_value("Site", site_name, ['is_renew']):
        parent_doc = frappe.get_doc("Site", site_name)
        data = [row for row in parent_doc.get("site_subscription") if row.is_renew == 1][0]
        return frappe.db.get_value("Subscription", data.subscription, ['end_date']).strftime('%d-%m-%Y')
    else:
        return date.strftime('%d-%m-%Y')

def get_plan(subscription_name, site_name):
    if frappe.db.get_value("Site", site_name, ['is_renew']):
        parent_doc = frappe.get_doc("Site", site_name)
        data = [row for row in parent_doc.get("site_subscription") if row.is_renew == 1][0]
        sql = f""" SELECT plan FROM `tabSubscription Plan Detail` WHERE parent=%s"""
        plan = frappe.db.sql(sql, (data,), as_dict=True)
        if plan:
            return plan[0].get('plan')
    else:
        sql = f""" SELECT plan FROM `tabSubscription Plan Detail` WHERE parent=%s"""
        plan = frappe.db.sql(sql, (subscription_name,), as_dict=True)
        if plan:
            return plan[0].get('plan')