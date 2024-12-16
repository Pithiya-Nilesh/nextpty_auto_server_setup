from time import sleep
from frappe.utils.password import get_decrypted_password
from nextpty_auto_server_setup.apis.site import set_frappe_cloud_logs
import frappe, json, requests
import boto3


@frappe.whitelist()
def create_dns_record_and_add_domain(site, parent=""):
    domain = f"{site}.nextpty.com"
    site_name = f"{site}.frappe.cloud"
    
    aws_settings = frappe.get_doc("Route53 Settings", "Route53 Settings")
    HOSTED_ZONE_ID = aws_settings.hosted_zone_id
    aws_access_key_id = get_decrypted_password("Route53 Settings", "Route53 Settings", 'aws_access_key_id', raise_exception=False)
    secret_access_key = get_decrypted_password("Route53 Settings", "Route53 Settings", 'aws_secret_access_key', raise_exception=False)
    region = aws_settings.default_region
    
    # client = boto3.client(
    #     'route53',
    #     aws_access_key_id = aws_access_key_id,
    #     aws_secret_access_key = secret_access_key,
    #     region_name = aws_settings.default_region
    # )
    frappe.log_error("Test Route53 credentials.", f"key: {aws_access_key_id}\nsecret: {secret_access_key}\nregion: {region}\nhosted zone id: {HOSTED_ZONE_ID}")

    session = boto3.Session(
        aws_access_key_id=aws_access_key_id,
        aws_secret_access_key=secret_access_key,
        region_name=region
    )

    client = session.client('route53')
    
    cname_response = create_dns_record(
        record_type='CNAME',
        name= f"{domain}.",
        value= f"{site_name}.",
        HOSTED_ZONE_ID=HOSTED_ZONE_ID,
        client=client
    )
    print("\n\n type", type(cname_response))
    print("CNAME Record Response:", cname_response)
    
    data = {
        "domain": domain,
        "site_name": site_name,
        "record_type": "CNAME",
        "parent": parent
    }
    
    status_code = cname_response.get('ResponseMetadata', {}).get('HTTPStatusCode')
    change_status = cname_response.get('ChangeInfo', {}).get('Status')

    if status_code == 200:
        if change_status == "EXIST":
            set_frappe_cloud_logs("Failed", site, data, cname_response, "Add CNAME Record")
            return {"status": False, "response": cname_response}
        
        elif change_status == "PENDING":
            cname_response = serialize_response(cname_response)
            set_frappe_cloud_logs("Success", site, data, cname_response, "Add CNAME Record")
            sleep(30)
            frappe.enqueue("nextpty_auto_server_setup.apis.site_domain.add_domain", site_name=site_name, domain=domain, site=site)
            # add_domain(site_name, domain, site)
            return {"status": True, "response": cname_response}

    set_frappe_cloud_logs("Failed", site, data, cname_response, "Add CNAME Record")
    return {"status": False, "response": cname_response}


    # a_record_response = create_dns_record(
    #     record_type='A',
    #     name= f"{domain}.",
    #     value= '3.84.240.128'
    # )
    # print("A Record Response:", a_record_response)
    
    # check_dns(domain, site)


@frappe.whitelist()
def check_dns(domain, site_name):
    # press.api.site.check_dns
    
#     {
#     "message": {
#         "CNAME": {
#             "type": "CNAME",
#             "matched": false,
#             "answer": "The DNS query name does not exist: XGSD."
#         },
#         "type": "A",
#         "matched": false,
#         "answer": "The DNS query name does not exist: XGSD.",
#         "A": {
#             "type": "A",
#             "matched": false,
#             "answer": "The DNS query name does not exist: XGSD."
#         }
#     }
# }

    try:       
        frappe_credentials = frappe.get_single("Frappe Cloud Credentials")
        
        url = f"{frappe_credentials.url}/api/method/press.api.site.check_dns"
        
        headers = {
            "X-Press-Team": frappe_credentials.team,
            "Authorization": f"""token {frappe_credentials.api_key}:{get_decrypted_password("Frappe Cloud Credentials", "Frappe Cloud Credentials", "api_secret")}"""
        }
        
        data = {
            "name": site_name,
            "domain": domain
        }

        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            status = "Success"
            response = response.text
        else:
            status = "Failed"
            response = response.text
            
        add_domain(site_name, domain)
        set_frappe_cloud_logs(status, site_name, data, response, "Add Domain")
        
    except Exception as e:
        frappe.log_error("Error: While Checking DNS For a Site In Frappe Cloud", f"Error: {e}\nsite_name: {site_name}\ndomain: {domain}")


def create_dns_record(record_type, name, value, HOSTED_ZONE_ID, client, ttl=300):
    if record_exists(name, record_type, HOSTED_ZONE_ID, client):
        return {
            'ResponseMetadata': {
                'HTTPStatusCode': 200,
            },
            'ChangeInfo': 
            {
                'Status': 'EXIST',
                'Comment': f'site "{name}" is already exist try another one.'
            }
        }
        
    else:
        response = client.change_resource_record_sets(
            HostedZoneId=HOSTED_ZONE_ID,
            ChangeBatch={
                'Comment': 'Create {} record'.format(record_type),
                'Changes': [
                    {
                        'Action': 'CREATE',
                        'ResourceRecordSet': {
                            'Name': name,
                            'Type': record_type,
                            'TTL': ttl,
                            'ResourceRecords': [{'Value': value}]
                        }
                    }
                ]
            }
        )
        return response

def record_exists(name, record_type, HOSTED_ZONE_ID, client):
    try:
        response = client.list_resource_record_sets(
            HostedZoneId=HOSTED_ZONE_ID,
            StartRecordName=name,
            StartRecordType=record_type,
            MaxItems="1"
        )
        record_sets = response.get('ResourceRecordSets', [])
        for record in record_sets:
            if record['Name'] == f"{name}" and record['Type'] == record_type:
                return True
        return False
    except Exception as e:
        frappe.log_error("Error: While check CNAME record is exist or not", f"{e}\nname: {name}\nrecord_type: {record_type}")


def serialize_response(response):
    if 'ChangeInfo' in response and 'SubmittedAt' in response['ChangeInfo']:
        response['ChangeInfo']['SubmittedAt'] = response['ChangeInfo']['SubmittedAt'].isoformat()
    return response


@frappe.whitelist()
def add_domain(site_name, domain, site):
    try:       
        frappe_credentials = frappe.get_single("Frappe Cloud Credentials")
        
        url = f"{frappe_credentials.url}/api/method/press.api.site.add_domain"
        
        headers = {
            "X-Press-Team": frappe_credentials.team,
            "Authorization": f"""token {frappe_credentials.api_key}:{get_decrypted_password("Frappe Cloud Credentials", "Frappe Cloud Credentials", "api_secret")}"""
        }
        
        data = {
            "name": site_name,
            "domain": domain
        }

        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 200:
            status = "Success"
            response = response.text
        else:
            status = "Failed"
            response = response.text
            
        set_frappe_cloud_logs(status, site, data, response, "Add Domain")
        
    except Exception as e:
        frappe.log_error("Error: While Adding Domain For a Site In Frappe Cloud", f"Error: {e}\nsite_name: {site_name}\ndomain: {domain}")


