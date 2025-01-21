import frappe


@frappe.whitelist()
def get_user_payments():
    user = frappe.session.user
    if user == "Guest":
        frappe.throw("You need to log in to view payment history.")
    payments = frappe.db.get_list(
        "Payment Entry",
        filters={"owner": user},
        fields=["name", "posting_date", "paid_amount", "reference_name"],
        order_by="posting_date desc"
    )
    print("\n\nPayments",payments)
    return payments

from frappe.utils.print_format import download_pdf

@frappe.whitelist()
def download_invoice(payment_entry_name):
    payment_entry = frappe.get_doc("Payment Entry", payment_entry_name)
    
    # Check if the logged-in user is the owner
    if frappe.session.user != payment_entry.owner:
        frappe.throw("You do not have permission to download this invoice.")

    try:
        # Generate the PDF content
        pdf_content = download_pdf(
            doctype="Payment Entry",
            name=payment_entry_name,
            format=None,  # Ensure this format exists
            no_letterhead=1,    # Use this only if letterhead is not required
        )

        if not pdf_content:
            frappe.throw("Failed to generate PDF. Please check the print format.")

        # Set up the response for file download
        frappe.local.response.filecontent = pdf_content
        frappe.local.response.filename = f"Invoice_{payment_entry_name}.pdf"
        frappe.local.response.type = "download"

    except Exception as e:
        frappe.log_error(f"Error in download_invoice: {str(e)}", "PDF Generation Error")
        frappe.throw("An error occurred while generating the invoice. Please contact support.")

     
def create_payment_for_site(plan, subscription_type, site, token, is_trial=0, user=frappe.session.user, is_new=0, save_card=1):
    from nextpty_auto_server_setup.www.payment import create_payment
    return create_payment(plan, subscription_type, site, token, is_trial, user=frappe.session.user, is_new=0, save_card=0)
