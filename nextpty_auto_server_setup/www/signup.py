from datetime import datetime, timedelta
import re
import frappe, json
import requests



@frappe.whitelist(allow_guest=True)
def signup(formdata):
    recaptcha_response = formdata.get('recaptcha_response')
    if not verify_recaptcha(recaptcha_response):
        frappe.throw("reCAPTCHA verification failed. Please try again.")

    data = json.loads(formdata)
    site_name = re.sub(r'[^a-zA-Z0-9-]', '', data["site_name"].lower().replace(" ", "-"))
    
    if len(site_name) < 5:
        return frappe.throw(msg="site name is too short. use 5 or more characters.", title="site name is too short.")
    
    if site_exist(site_name):
        return frappe.throw(title=frappe._("Site Already Exists."), msg=frappe._("Your Site Name is Alredy Exists. Please Enter Another Site Name"))
    
    user = create_user(data)
    if user:
        customer = create_customer(data, user)
        if customer:
            subscription = create_subscription(data, customer)
            if subscription:
                if create_site_record(data['site_name'], subscription):
                    if create_customer_site_details_record(data, customer):
                        frappe.msgprint(title=frappe._('Your site creation is in progress...'), msg=frappe._(f"Soon, we will share the credentials and the URL of your site with you via email at {data['contact_email']}."))

@frappe.whitelist()
def site_exist(site_name):
    query = """
        SELECT site_name 
        FROM `tabSite Details` 
        WHERE site_name = %s AND status != 'Dropped'
    """
    result = frappe.db.sql(query, (site_name,), as_dict=True)
    return True if result else False


def create_user(data):
    try:
        if frappe.db.exists("User", data['contact_email']):
            return frappe.db.get_value("User", filters={"name": data['contact_email']}, fieldname=['name'])
        else:
            doc = frappe.get_doc({
                "doctype": "User",
                "email": data['contact_email'],
                "first_name": data['company_name'],
                "send_welcome_email": 0,
                "enabled": 1,        
                "roles": [
                    { "role": "Customer"}
                ]
            })
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            return doc.name
            
    except Exception as e:
        frappe.log_error("Error: While creating user", f"Error: {e}\ndata: {data}")
        frappe.throw(title=frappe._("Somthing want wrong"), msg=e)
        return False


def create_customer(data, user):
    try:       
        # docname = frappe.db.get_value("Customer", {"customer_name": data['company_name']}, fieldname=['name'])
        # if docname:
        #     doc = frappe.get_doc("Customer", docname)
        # else:
        #     doc = frappe.new_doc("Customer")
        #     doc.customer_name = data['company_name']
        
        doc = frappe.new_doc("Customer")
        doc.customer_name = data['company_name']
        existing_portal_user = next((u for u in doc.portal_users if u.user == user), None)
        if not existing_portal_user:
            doc.append('portal_users', {
                'user': user
            })
        
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return frappe.db.get_value("Customer", filters={"customer_name": data['company_name']}, fieldname=['name'])

            
    except Exception as e:
        frappe.log_error("Error: While Creating Customer", f"Error: {e}\ndata: {data}")
        frappe.throw(msg=e, title=frappe._("Somthing Want wrong"))


def create_subscription(data, customer, plan="Trial", is_trial=1, subscription_type="monthly"):
    try:
        doc = frappe.new_doc("Subscription")
        doc.party_type = "Customer"
        doc.party = customer
        if is_trial:
            doc.trial_period_start = datetime.today().strftime('%Y-%m-%d')
            trial_period_end_date = datetime.today() + timedelta(days=60)
            doc.trial_period_end = trial_period_end_date.strftime('%Y-%m-%d')
        else:
            doc.start_date = datetime.today().strftime('%Y-%m-%d')
            if subscription_type == "monthly":
                doc.end_date = datetime.today() + timedelta(days=31)
            elif subscription_type == "yearly":
                doc.end_date = datetime.today() + timedelta(days=366)


        doc.append('plans', {
            'plan': plan,
            'qty': 1
        })
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        return doc.name
    
    except Exception as e:
        frappe.log_error("Error: While Creating Subscription", f"Error: {e}\ndata: {data}\ncustomer: {customer}\nplan: {plan}\nis_trial: {is_trial}\nsubscription_type: {subscription_type}")
        frappe.throw(msg=e, title=frappe._("Somthing Want Wrong!"))
        return False


def create_site_record(site_name, subscription, is_trial=1, is_active=1):
    try:
        docname = frappe.db.get_value("Site", filters={"name": site_name}, fieldname=['name'])
        if docname:
            doc = frappe.get_doc("Site", docname)
        else:
            doc = frappe.new_doc("Site")
            doc.site_name = site_name
            
        doc.append('site_subscription', {
            "subscription": subscription,
            "is_trial": is_trial,
            "is_active": is_active
        })
        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return True
    
    except Exception as e:
        frappe.log_error("Error: White creating site record", f"Error: {e}\nsite_name: {site_name}\nsubscription: {subscription}")
        return False


def create_customer_site_details_record(data, customer):
    try:
        # docname = frappe.db.get_value("Customer Site Details", {"customer": customer}, fieldname=['name'])
        # if docname:
        #     doc = frappe.get_doc("Customer Site Details", docname)
        # else:
        #     doc = frappe.new_doc("Customer Site Details")
        #     doc.customer = customer
        
        doc = frappe.new_doc("Customer Site Details")
        doc.customer = customer
        
        existing_contact = next((contact for contact in doc.contact_details if contact.contact_email == data['contact_email']), None)

        if not existing_contact:
            doc.append('contact_details', {
                "contact_email": data['contact_email'],
                "contact_name": data['contact_name']
            })
            
        existing_site = next((site for site in doc.site_details if site.site_name == data['site_name']), None)
        if not existing_site:
            doc.append("site_details", {
                "site_name": data['site_name'],
                "site_owner_email": data['contact_email']
            })

        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return True
    
    except Exception as e:
        frappe.log_error("Error: While Creating Site Details  Record", f"Error: {e}\ndata: {data}\ncustomer: {customer}")
        frappe.throw(msg=e, title=frappe._("Somthing Want Wrong!"))
        return False


@frappe.whitelist(allow_guest=True)
def get_logged_in_user_details(user=""):
    try:
        user = frappe.session.user if not user else user
        c_data = frappe.db.sql(f""" SELECT parent FROM `tabPortal User` WHERE user="{user}" """, as_dict=True)
        u_data = frappe.db.get_value("User", filters={'email': user}, fieldname=['first_name'])
        if c_data:
            data = {'customer': c_data[0]['parent'], 'contact_name': u_data, 'contact_email': user}
        else:
            data = {'customer': "", 'contact_name': "", 'contact_email': ""}
        return data
    except Exception as e:
        frappe.log_error("Error: While get logged in user data", f"Error: {e}\nuser: {user}")


def verify_recaptcha(recaptcha_response):
    secret_key = "6LdGT6YqAAAAAAU9GUCEh-mml3yZ-38eZN9DOW" 
    payload = {
        'secret': secret_key,
        'response': recaptcha_response
    }
    response = requests.post("https://www.google.com/recaptcha/api/siteverify", data=payload)
    result = response.json()
    return result.get('success', False)