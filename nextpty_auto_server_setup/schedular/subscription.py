
import frappe
from frappe.utils import today
from datetime import datetime,timedelta
from frappe.utils.data import nowdate
from frappe.utils.password import get_decrypted_password
from nextpty_auto_server_setup.apis.payment import create_payment_for_site
from nextpty_auto_server_setup.apis.site import activate_site
from nextpty_auto_server_setup.www.signup import create_subscription


@frappe.whitelist()
def check_and_deactivate_expired_subscription_sites():
    try:
        # subscription_end_sites = []
        # trial_subscription_end_sites = []
        
        subscription_end_sites = (get_subscription_end_sites())
        trial_subscription_end_sites = (get_trial_subscription_end_sites())
        
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
            if check_auto_renew(site_name):
                continue
            else:
                return deactivate_site(site_name)
   

def deactivate_trial_subscription_end_sites(trial_subscription_end_sites):
    from nextpty_auto_server_setup.apis.site import deactivate_site
    if trial_subscription_end_sites:
        for site_name in trial_subscription_end_sites:
            if check_auto_renew(site_name):
                continue
            else:
                return deactivate_site(site_name)

def check_auto_renew(site_name):
    site_data = frappe.get_all("Site Subscription",filters={"parent":site_name, "parenttype":"Site"},fields=["subscription","is_active","is_trial","creation"])
    if site_data:
        last_subscription_data = sorted(site_data, key=lambda x: x["creation"], reverse=True)[0]
        
        cancelled = frappe.db.get_value("Subscription", last_subscription_data["subscription"], ["custom_is_cancelled"])
        saved_card = frappe.db.get_value("Croem Saved Card Token", filters={"user": frappe.session.user, "site_name": site_name}, fieldname=['name'])
        if cancelled or not saved_card:
            return False
        else:
            token = get_decrypted_password("Croem Saved Card Token", saved_card, "token") or ""
            res = create_payment_for_site("HOSTING STANDARD", "monthly", site_name, token, is_trial=0, user=frappe.session.user, is_new=0, save_card=0)
            return True if res.get('status') == "Success" else False
    else:
        return False

@frappe.whitelist()
def re_new_subscription(site, subscription_type, plan, is_trial=0):
    """ re active site subscription 
        params: 
        site = sitename in frappe doc,
        subscription_type = e.g. monthly, yearly etc.
        plan = e.g. gold, platinum, trial etc.
        is_trial = if this is a trial period or give any trial to customer using coupon code or etc.
    """
    try:
        is_trial = 1 if plan == "Trial" else 0
        
        SUBSCRIPTION_TYPES = ["monthly", "yearly"]
        if not subscription_type in SUBSCRIPTION_TYPES:
            return frappe.throw("Invalid Subscription Type", "Subscription type must be monthly or yearly.")
        
        site_name = frappe.db.get_value("Site", filters={"name": site}, fieldname=['name'])
        if not site_name:
            return frappe.throw("Site Not Found", "We not found any record of your site.")

        sql = """
            SELECT p.customer 
            FROM `tabCustomer Site Details` AS p
            INNER JOIN `tabSite Details` AS c 
            ON c.parent = p.name
            WHERE c.site_name = %s
        """
        customer = frappe.db.sql(sql, (site,), as_dict=True)
        if customer:
            if 'customer' in customer[0]:
                customer = customer[0]['customer']
                subscription = create_subscription("re-active subscription", customer, plan, is_trial, subscription_type)
                if subscription:
                    doc = frappe.get_doc("Site", site)
                    for i in doc.site_subscription:
                        i.is_active = 0
                    doc.save(ignore_permissions=True)
                    doc.append('site_subscription', {
                        'subscription': subscription,
                        'is_trial': is_trial,
                        'is_active': 1
                    })
                    doc.save(ignore_permissions=True)
                    frappe.db.commit()
                    active = activate_site(site)
                    if active:
                        frappe.msgprint(title= "Success", message= "Your Site Subscription is renewed", indicator= "green")
                        return True
            else:
                frappe.throw("Customer Not Found", "Customer not found for this site.")
                return False
        else:
            frappe.throw("Customer Not Found", "Customer not found for this site.")
            return False

             
    except Exception as e:
        frappe.log_error("Error: While re new subscription for site.", f"Error: {e}\nsite: {site}\nsubscription_type: {subscription_type}\nplan: {plan}\nis_trial: {is_trial}")
        return False
    
@frappe.whitelist()
def check_and_send_mail_for_expiring_subscription():
    print()
    from datetime import datetime, timedelta
    import pdb
    pdb.set_trace()

    subscriptions = frappe.get_all("Subscription", fields=["name","status", "party", "end_date","trial_period_end"])
    today_date = datetime.today().date()

    for subscription in subscriptions:
        try:
            if subscription.get("status") == "Trialling":
                end_date = subscription.get("trial_period_end")
            else:
                end_date = subscription.get("end_date")

            if not end_date:
                frappe.log_error(
                    f"Subscription {subscription.get('name')} has no valid end date.",
                    "Missing end date in Subscription"
                )
                continue

            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, "%Y-%m-%d").date()

            if today_date <= end_date <= (today_date + timedelta(days=3)):
                site_details = frappe.get_all(
                    "Site Subscription",  
                    filters={"subscription": subscription.get("name")},
                    fields=["parent"]
                )

                for site in site_details:
                    site_data = frappe.get_all(
                        "Site Details", 
                        filters={"site_name": site.get("parent")},
                        fields=["parent", "site_owner_email","site_name"]
                    )

                    for detail in site_data:

                            subject = f"Subscription Expiring Soon: {subscription.get('name')}"
                            message = f"""
                                <p>Dear,</p>
                                <p>Your subscription <b>{subscription.get('name')}</b> for site {detail.get("site_name")} is set to expire soon.</p>
                                <p>Please renew your subscription to avoid service interruption.</p>
                                <p>Thank you,</p>
                                <p>Your Team</p>
                            """
                            print("\n\nAre we sending mail???")
                            frappe.sendmail(
                                recipients=[detail.get("site_owner_email")],
                                subject=subject,
                                message=message
                            )

        except Exception as e:
            # Log errors with detailed context
            frappe.log_error(
                f"Error while processing subscription: {subscription.get('name')}",
                f"Exception: {str(e)}\nSubscription Data: {subscription}"
            )


                # email_addresses = frappe.get_all("Portal User",filters={'parent':entry.get("party")},fields=["email"])

                # recipients = [user.get("email") for user in email_addresses if user.get("email")]

                # if recipients:
                #     subject=f"Subscription Expiring Soon:{entry.get('name')}"
                #     message=f"""
                #         <p>Dear {entry.get('party')},</p>
                #         <p>Your subscription <b>{entry.get('name')}</b> is set to expire on <b>{end_date}</b>.</p>
                #         <p>Please renew your subscription to avoid service interruption.</p>
                #         <p>Thank you,</p>
                #         <p>Your Team</p>
                #     """

                #     frappe.sendmail(
                #         recipients=recipients,
                #         subject=subject,
                #         message=message
                #     )
                
@frappe.whitelist()
def cancel_subscription(subscription_name, site_name):
    s_user = frappe.session.user
    try:
        frappe.set_user("Administrator")
        doc = frappe.get_doc("Subscription", subscription_name)
        doc.status = "Cancelled"
        doc.cancelation_date = nowdate()
        doc.custom_is_cancelled = 1
        doc.save()
        frappe.db.commit()
        
        d = frappe.db.get_value("Croem Saved Card Token", filters={"user": s_user, "site_name": site_name}, fieldname=['name'])
        if d:
            saved_data = frappe.get_doc("Croem Saved Card Token", d)
            saved_data.delete()
            frappe.db.commit()
        frappe.set_user(s_user)

    except Exception as e:
        frappe.log_error("Error: While cancel subscription", f"Error: {e}\nsubscription_name: {subscription_name}")
        frappe.set_user(s_user)
