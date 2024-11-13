import frappe

import frappe
from frappe import _
from nextpty_auto_server_setup.webhooks.site_status_change import site_status_change


@frappe.whitelist(allow_guest=True)
def webhook():
    # secret = frappe.request.headers.get('X-Webhook-Secret', "")
    # if secret != frappe.db.get_single_value("Frappe Cloud Credentials", "super_secret"):
    #     frappe.log_error("unorthorised", frappe.request.get_json())
    #     frappe.respond_as_web_page(_("Unauthorized"), http_status_code=401)

    
    # Handle the webhook validation event (sent by FC for verification)
    event = payload.get('event')
    if event == "Webhook Validate":
        return "Validated"
    
    payload = frappe.request.get_json()
    
    if event == "Site Status Update":
        return site_status_change(payload)
