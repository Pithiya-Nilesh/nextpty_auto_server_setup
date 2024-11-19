
import frappe
from frappe.utils import today
from datetime import datetime


@frappe.whitelist()
def check_and_deactivate_expired_subscription_sites():
    try:
        subscription_end_sites = []
        trial_subscription_end_sites = []
        
        subscription_end_sites.append(get_subscription_end_sites())
        trial_subscription_end_sites.append(get_trial_subscription_end_sites())
        
        deactivate_subscription_end_sites(subscription_end_sites)
        deactivate_trial_subscription_end_sites(trial_subscription_end_sites)
        
    except Exception as e:
        frappe.log_error("Error: While get expired subscription sites", f"Error: {e}")


def get_subscription_end_sites():
    site_names = [] 
    subscriptions = frappe.get_all("Subscription", fields=["name", "party", "end_date"])
    
    for entry in subscriptions:
        try:
            values = {
                "subscription_name": entry.get("name", ""),
                "end_date": entry.get("end_date", ""), 
                "date": today()
            }
            
            date_to_compare = datetime.strptime(values['date'], "%Y-%m-%d").date()
            
            if values["end_date"] and date_to_compare == values["end_date"]:
                parent_sites = frappe.db.get_all(
                    "Site Subscription", 
                    filters={"subscription": values["subscription_name"]},
                    fields=["name", "parent", "is_active"]
                )
                
                if parent_sites:
                    for site in parent_sites:
                        frappe.db.set_value(
                            "Site Subscription", 
                            site["name"], 
                            "is_active", 
                            0
                        )
                        site_names.append(site["parent"])
        except Exception as e:
            frappe.log_error("Error: While get subscription end sites", f"Error: {e}\nentry: {entry}\nentry name: {entry.name}")
    
    frappe.db.commit()
    return site_names


def get_trial_subscription_end_sites():
    site_names = [] 
    subscriptions = frappe.get_all("Subscription", fields=["name", "party", "trial_period_end"])
    
    for entry in subscriptions:
        try:
            values = {
                "subscription_name": entry.get("name", ""),
                "trial_end_date": entry.get("trial_period_end", ""), 
                "date": today()
            }
            
            date_to_compare = datetime.strptime(values['date'], "%Y-%m-%d").date()
            
            if values["trial_end_date"] and date_to_compare == values["trial_end_date"]:
                parent_sites = frappe.db.get_all(
                    "Site Subscription", 
                    filters={"subscription": values["subscription_name"]},
                    fields=["name", "parent", "is_active"]
                )
                
                if parent_sites:
                    for site in parent_sites:
                        frappe.db.set_value(
                            "Site Subscription", 
                            site["name"], 
                            "is_active", 
                            0
                        )
                        site_names.append(site["parent"])
        except Exception as e:
            frappe.log_error("Error: While get trial end sites", f"Error: {e}\nentry: {entry}\nentry name: {entry.name}")

    frappe.db.commit()  
    return site_names


def deactivate_subscription_end_sites(subscription_end_sites):
    from nextpty_auto_server_setup.apis.site import deactivate_site
    if subscription_end_sites:
        for site_name in subscription_end_sites:
            return deactivate_site(site_name)
   

def deactivate_trial_subscription_end_sites(trial_subscription_end_sites):
    from nextpty_auto_server_setup.apis.site import deactivate_site
    if trial_subscription_end_sites:
        for site_name in trial_subscription_end_sites:
            return deactivate_site(site_name)
