import json
import frappe
import frappe.utils
from frappe.utils.password import get_decrypted_password
from nextpty_auto_server_setup.schedular.subscription import re_new_subscription
import requests
import xml.etree.ElementTree as ET



@frappe.whitelist(allow_guest=True)
def get_payment_popup(user=frappe.session.user):
    try:
        settings = frappe.get_doc("Croem Settings")
        if not settings.enable:
            frappe.throw("Please Enable Croem Settings", "Croem Settings Not Enable") 
        widget_url = ""
        if settings.use_sandbox:
            widget_url = settings.widget_sandbox_url
        else:
            widget_url = settings.widget_production_url
        
        token = ""
        # if frappe.db.get_value("Croem Save Token", user, fieldname=['name']):
        #     token = get_decrypted_password("Croem Save Token", user, "token")
        
        params = {
            "APIKey": get_decrypted_password("Croem Settings", "Croem Settings", "api_key") or "",
            "Token": token,
            "Culture": ""
        }
        try:
            response = requests.get(widget_url, params=params)
            response.raise_for_status()
            
            return {"html": response.text}
        except requests.exceptions.RequestException as e:
            frappe.log_error(f"Error fetching payment form: {str(e)}", "Payment Form Fetch Error")
            frappe.throw("An error occurred while fetching the payment form. Please try again later.")
    except Exception as e:
        frappe.log_error("Error: While get croem popup html", f"Error: {e}\nuser: {user}")


@frappe.whitelist(allow_guest=True)
def create_payment(plan, subscription_type, site, popup_response, is_trial=0, user=frappe.session.user, is_new=0):
    try:
        popup_response = json.loads(popup_response)
        
        save_card_details(user, popup_response)
        
        settings = frappe.get_doc("Croem Settings")
        if not settings.enable:
            frappe.throw("Please Enable Croem Settings", "Croem Settings Not Enable")
        transaction_url = ""
        if settings.use_sandbox:
            transaction_url = settings.transaction_sandbox_url
        else:
            transaction_url = settings.transaction_production_url
        
        token = popup_response.get("AccountToken")
        amount = 10
        
        # token = ""
        # if frappe.db.get_value("Croem Save Token", user, fieldname=['name']):
        #     token = get_decrypted_password("Croem Save Token", user, "token")

        soap_body = f'''<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:tem="http://tempuri.org/">
        <soapenv:Header/>
        <soapenv:Body>
            <tem:Sale>
                <tem:APIKey>{get_decrypted_password("Croem Settings", "Croem Settings", "api_key") or ""}</tem:APIKey>
                <!-- <tem:accessCode>123123</tem:accessCode> -->
                <tem:merchantAccountNumber>{settings.midmerchant}</tem:merchantAccountNumber>
                <tem:terminalName>{settings.tidterminal}</tem:terminalName>
                <tem:accountToken>{token}</tem:accountToken>
                <tem:clientTracking>Pruebas</tem:clientTracking>
                <tem:amount>{amount}</tem:amount>
                <tem:currencyCode>840</tem:currencyCode>
            </tem:Sale>
        </soapenv:Body>
        </soapenv:Envelope>'''


        # Headers
        headers = {
            'Content-Type': 'text/xml'
        }

        # Make the POST request
        response = requests.post(transaction_url, headers=headers, data=soap_body)

        # Print the response
        print("Response Status Code:", response.status_code)
        print("Response Text:", response.text)
        namespace = {"soap": "http://schemas.xmlsoap.org/soap/envelope/", "temp": "http://tempuri.org/"}
        root = ET.fromstring(response.text)

        # Find the <Description> element
        description = root.find(".//temp:Description", namespace)

        # Check if the description is "Approved"
        if description is not None and description.text == "Approved":
            print("The description is Approved.")
            if not is_new:
                if re_new_subscription(site, subscription_type, plan, is_trial=0):
                    return {"status": "Success"}
            else:
                return {"status": "Success"}
        else:
            print("The description is not Approved or not found.")
            {"status": "Failed", "msg": response.text}
        
    except Exception as e:
        frappe.log_error("Error: While Create Payment", f"Error: {e}")
        {"status": "Failed", "msg": e}
    
# SUCCESS RESPONSE
"""  
<?xml version="1.0" encoding="utf-8"?>
<soap:Envelope xmlns:soap="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:xsd="http://www.w3.org/2001/XMLSchema">
    <soap:Body>
        <SaleResponse xmlns="http://tempuri.org/">
            <SaleResult>
                <ExtensionData />
                <TransactionId>103369105</TransactionId>
                <OperationType>Sale</OperationType>
                <Tracking>Pruebas</Tracking>
                <RequestDate>2025-01-20T00:18:35.4235733-05:00</RequestDate>
                <ResponseDate>2025-01-20T00:18:35.7673335-05:00</ResponseDate>
                <Code>00</Code>
                <BinId>1</BinId>
                <AuthorizationNumber>9999999999</AuthorizationNumber>
                <ProcessorId>2</ProcessorId>
                <Description>Approved</Description>
                <Result>00~0~0~0~0~103369105~</Result>
                <InternalResponseCode>0</InternalResponseCode>
            </SaleResult>
        </SaleResponse>
    </soap:Body>
</soap:Envelope>
"""

def save_card_details(user, popup_response):
    try:
        doc = frappe.new_doc("Croem Saved Card Token")
        doc.user = user
        doc.token = popup_response.get("AccountToken")
        doc.account_number = popup_response.get("AccountNumber")
        doc.card_holder_name = popup_response.get("CardHolderName")
        doc.card_number = popup_response.get("CardNumber")
        doc.insert(ignore_permissions=True)
        frappe.db.commit()
        
    except Exception as e:
        frappe.log_error("Error: While save card details", f"Error: {e}\nuser: {user}\npopup_response: {popup_response}")
