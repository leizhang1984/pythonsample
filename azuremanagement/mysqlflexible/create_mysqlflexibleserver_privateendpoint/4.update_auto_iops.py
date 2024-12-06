import os
import json
from asyncio import sleep

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.rdbms.mysql_flexibleservers import MySQLManagementClient
import requests

'''
https://learn.microsoft.com/en-us/rest/api/mysql/flexibleserver/servers/create?view=rest-mysql-flexibleserver-2024-06-01-preview&tabs=HTTP
'''

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')


    #这里要设置PE订阅ID
    pe_subscription_id = "c4959ac6-4963-4b67-90dd-da46865b607f"

    #DD的订阅ID
    dd_subscription_id = "074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb"

     #资源组名称
    rgname = "defaultrg"

    #MySQl Flexible Server服务器名称，需要和上面的Private DNS Zone名称一致
    mysqlflexible_servername = "leizhangproduction-00"

    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    # Create MySQL Client
    mysqlflexiblesvr_client = MySQLManagementClient(
        credential=clientcredential,
        subscription_id=pe_subscription_id
    )

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

    #2.获得MySQL Flexible Server的资源ID
    mysql_client = mysqlflexiblesvr_client.servers.get(rgname,mysqlflexible_servername)


    #3.需要请求的JSON Body
    data= {
        "properties": {
            "storage": {
                #设置自动IO
                "autoIoScaling": "Enabled"
            }
        },
        "location": "Germany West Central"
    }

    #4.Update
    put_url = f"https://management.azure.com/{mysql_client.id}?api-version=2024-06-01-preview"
    headers = {'Authorization': f'Bearer {access_token}'}
    put_response  = requests.put(put_url,headers = headers,json=data)

    async_operation_url = put_response.headers['Azure-AsyncOperation']
    while check_async_status(access_token,async_operation_url) != 'Succeeded':
        print("没有执行成功")
        sleep(1)
    
    print("执行成功")

def check_async_status(access_token,async_operation_url):
    #https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/async-operations
    get_url = async_operation_url
    headers = {'Authorization': f'Bearer {access_token}'}

    get_response = requests.get(get_url,headers = headers)
    get_response_data = get_response.json()
    return get_response_data['status']

if __name__ == "__main__":
    main()