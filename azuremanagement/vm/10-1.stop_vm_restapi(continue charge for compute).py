import requests
import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient

tenantid = os.environ.get('nonprod_tenantid')
clientid = os.environ.get('nonprod_clientid')
clientsecret = os.environ.get('nonprod_clientsecret')

def main():
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    compute_client = ComputeManagementClient(
        credential = clientcredential,
        subscription_id = subscription_id
    )

    #获得虚拟机的资源ID
    vmid = compute_client.virtual_machines.get("lab-rg", "privatevm2019").id

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

    #执行关机操作
    #参考URL: https://learn.microsoft.com/en-us/rest/api/compute/virtual-machines/power-off?view=rest-compute-2024-03-01&tabs=HTTP
    post_url = f"https://management.azure.com/{vmid}/powerOff?api-version=2024-03-01"
    headers = {'Authorization': f'Bearer {access_token}'}

    response = requests.post(post_url,headers = headers)
    if response.status_code == 202:
        print("Power Off成功")



if __name__ == '__main__':
    main()