import os
import requests
import sys

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')
  
    # 1.先获得Access Token
    token_endpoint = f'https://login.microsoftonline.com/{tenantid}/oauth2/token'

    # Define the required parameters for the token endpoint
    data = {
        'grant_type': 'client_credentials',
        'client_id': clientid,
        'client_secret': clientsecret,
        'resource': 'https://management.azure.com/'
    }
    # Make a request to the token endpoint to obtain an access token
    response = requests.post(token_endpoint, data=data)
    # 获得Access Token
    access_token = response.json()['access_token']

    #2.再获得Application Gateway的资源ID
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    rg_name = "FW-Hybrid-Test"
    applicationgateway_name = "leiappgw01"
    
    #后端池需要删除的IP地址
    remove_ip = "10.99.2.7"

    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    network_client = NetworkManagementClient(credential=clientcredential,subscription_id=subscription_id)
    application_gateway = network_client.application_gateways.get(rg_name,applicationgateway_name)
    
    #3.拿到Application的所有属性
    get_url = f"https://management.azure.com/{application_gateway.id}?api-version=2022-09-01"
    headers = {'Authorization': f'Bearer {access_token}'}
    get_response = requests.get(get_url,headers = headers)

    get_json_data = get_response.json()

    ips = get_json_data['properties']['backendAddressPools'][0]['properties']['backendAddresses']

    #遍历Application Gateway后端的所有IP
    for ip in ips:
        #如果找到这个IP
        if ip['ipAddress'] == remove_ip:
            #把这个IP删除掉
            ips.remove(ip)
    

    #4.把更新好的信息，重新提交
    put_url = f"https://management.azure.com/{application_gateway.id}?api-version=2022-09-01"
    headers = {'Authorization': f'Bearer {access_token}'}
    put_response = requests.put(put_url,headers = headers,json=get_json_data)
    print(put_response.status_code)


if __name__ == "__main__":
    main()