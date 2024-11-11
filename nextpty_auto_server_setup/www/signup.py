import frappe, json


@frappe.whitelist()
def signup(formdata):
    data = json.loads(formdata)
    # if site_exist(data):
    #   return frappe.throw(frappe._("Site Already Exists."), title=frappe._("Your Site Name is Alredy Exists. Please Enter Another Site Name"))
    if create_user(data):
        customer = create_customer(data)
        if customer:
            if create_site_record(data, customer):
                frappe.msgprint(title=frappe._('Success'), msg=frappe._("Your site creation is in progress..."))


def site_exist(data):
    site_name = data["site_name"]
    query = """
        SELECT site_name 
        FROM `tabSite` 
        WHERE site_name = %s AND status != 'Dropped'
    """
    result = frappe.db.sql(query, (site_name,), as_dict=True)    
    return True if result else False
    

def create_user(data):
    try:
        if frappe.db.exists("User", data['contact_email']):
            return True
        else:
            doc = frappe.new_doc("User")
            doc.send_welcome_email = 0
            doc.email = data['contact_email']
            doc.first_name = data['company_name']
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            return True
            
    except Exception as e:
        frappe.log_error("Error: While creating user", f"Error: {e}\ndata: {data}")
        frappe.throw(title=frappe._("Somthing want wrong"), msg=e)
        return False



def create_customer(data):
    try:
        if frappe.db.exists("Customer", {"customer_name": f"{data['company_name']}"}):
            return frappe.db.get_value("Customer", filters={"customer_name": data['company_name']}, fieldname=['name'])
        else:
            doc = frappe.new_doc("Customer")
            doc.customer_name = data['company_name']
            doc.insert(ignore_permissions=True)
            frappe.db.commit()
            return frappe.db.get_value("customer", filters={"customer_name": data['company_name']}, fieldname=['name'])
            
    except Exception as e:
        frappe.log_error("Error: While Creating Customer", f"Error: {e}\ndata: {data}")
        frappe.throw(msg=e, title=frappe._("Somthing Want wrong"))



def create_site_record(data, customer):
    try:
        docname = frappe.db.get_value("Customer Site Details", {"customer": data['company_name']}, fieldname=['name'])
        if docname:
            doc = frappe.get_doc("Customer Site Details", docname)
        else:
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
            doc.append("site_details",{
                "site_name": data['site_name'],
                "subscription": ""
            })

        doc.save(ignore_permissions=True)
        frappe.db.commit()
        return True
    
    except Exception as e:
        frappe.log_error("Error: While Creating Site Record", f"Error: {e}\ndata: {data}\ncustomer: {customer}")
        frappe.throw(msg=e, title=frappe._("Somthing Want wrong"))
        return False
    
# {"company_name":"1","contact_name":"3","contact_email":"4@mail.com","site_name":"sdg"}