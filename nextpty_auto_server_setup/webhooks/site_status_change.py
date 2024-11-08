import frappe

def site_status_change(payload):
    data = payload.get('data')
