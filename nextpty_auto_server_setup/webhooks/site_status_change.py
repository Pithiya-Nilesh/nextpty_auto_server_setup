import frappe

import frappe
from frappe import _


@frappe.whitelist(allow_guest=True)
def site_status_change_webhook():

    secret = frappe.request.headers.get('X-Webhook-Secret', "")
    if secret != frappe.db.get_single_value("Frappe Cloud Credentials", "super_secret"):
        frappe.log_error("unorthorised", frappe.request.get_json())
        frappe.respond_as_web_page(_("Unauthorized"), http_status_code=401)

    payload = frappe.request.get_json()
    event = payload.get('event')
    data = payload.get('data')
    frappe.log_error("response", payload)

    # Print the event and data (for demo purposes)
    print(f"Event: {event}")
    print(f"Data: {data}")

    # Handle the webhook validation event (sent by FC for verification)
    if event == "Webhook Validate":
        frappe.log_error("ok", event)
        return "OK"

    else:
        frappe.log_error("no", event)
        return "No"

