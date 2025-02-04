# app/overrides.py
import frappe

def redirect_to_signup(login_manager):
    user = frappe.session.user

    # Debugging: Check if the hook is triggered
    frappe.logger().info(f"Login Hook Triggered for User: {user}")
    print(f"Login Hook Triggered for User: {user}")

    # Skip redirection for admin or specific roles
    if user == "Administrator" or "System Manager" in frappe.get_roles(user):
        return

    # Add dummy redirection to test
    # frappe.local.response["type"] = "redirect"
    frappe.local.response["location"] = "/signup"
