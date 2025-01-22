import frappe


@frappe.whitelist()
def get_user_payments():
    
    # Step 1: Get logged-in user's email
    user = frappe.session.user
    if user == "Guest":
        return {"error": "User not logged in"}

    # Step 2: Fetch customers linked to the logged-in user
    customers = frappe.get_all(
        "Portal User", 
        filters={"parenttype": "Customer", "user": user},
        fields=["parent"]
    )
    if not customers:
        return {"error": "No customers linked to the user"}

    customer_list = [c["parent"] for c in customers]

    # Step 3: Fetch subscriptions linked to the customers
    subscriptions = frappe.get_all(
        "Subscription",
        filters={"party": ["in", customer_list]},
        fields=["name"]
    )
    if not subscriptions:
        return {"error": "No subscriptions found for the customers"}

    subscription_list = [s["name"] for s in subscriptions]

    # Step 4: Fetch sales invoices linked to the subscriptions
    sales_invoices = frappe.get_all(
        "Sales Invoice",
        filters={"subscription": ["in", subscription_list]},
        fields=["name"]
    )
    if not sales_invoices:
        return {"error": "No sales invoices found for the subscriptions"}

    sales_invoice_list = [si["name"] for si in sales_invoices]

    # Step 5: Fetch payment entries linked to the sales invoices
    payment_entries = frappe.db.sql(
        """
        SELECT 
            pe.name, pe.posting_date, pe.paid_amount, pe.reference_no, pe.reference_date, pe.creation
        FROM 
            `tabPayment Entry` AS pe
        JOIN 
            `tabPayment Entry Reference` AS per
        ON 
            pe.name = per.parent
        WHERE 
            per.reference_name IN %s
        ORDER BY 
            pe.creation DESC
        """,
        (tuple(sales_invoice_list),),
        as_dict=True
    )
    if not payment_entries:
        return {"error": "No payment entries found for the sales invoices"}

    print("\n\n payment", payment_entries)
    return payment_entries
        

from frappe.utils.print_format import download_pdf, get_pdf

@frappe.whitelist()
def download_invoice(payment_entry_name):
    # Check if the logged-in user is authenticated
    s_user = frappe.session.user
    
    if frappe.session.user == "Guest":
        return frappe.throw("You do not have permission to download this invoice.")

    try:
        frappe.set_user("Administrator")
        # Validate the Payment Entry exists
        if not frappe.db.exists("Payment Entry", payment_entry_name):
            return frappe.throw("Payment Entry does not exist.")
        
        html = frappe.get_print("Payment Entry", payment_entry_name, print_format=None)
        pdf_content = get_pdf(html)

        # Send the PDF as a response
        frappe.set_user(s_user)
        frappe.local.response.filename = f"{payment_entry_name}.pdf"
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.type = "download"


    except Exception as e:
        # Log the error for debugging
        frappe.log_error(message=str(e), title="PDF Generation Error")
        frappe.throw("An error occurred while generating the invoice. Please contact support.")
    
    finally:
        frappe.set_user(s_user)

    
 
def create_payment_for_site(plan, subscription_type, site, token, is_trial=0, user=frappe.session.user, is_new=0, save_card=1):
    from nextpty_auto_server_setup.www.payment import create_payment
    return create_payment(plan, subscription_type, site, token, is_trial, user=frappe.session.user, is_new=0, save_card=0)
