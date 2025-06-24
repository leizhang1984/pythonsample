import os
import requests
#pip3 install msgraph-sdk
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.applications.applications_request_builder import ApplicationsRequestBuilder

#列出所有的Service Principal
#需要的权限，请参考：
#https://learn.microsoft.com/en-us/graph/api/serviceprincipal-list?view=graph-rest-1.0&tabs=http#code-try-1
#Application.Read.All

def main():
    tenantid = os.environ.get('msdn_tenantid')
    clientid = os.environ.get('msdn_clientid')
    clientsecret = os.environ.get('msdn_clientsecret')

    # 1.先获得Access Token
    token_endpoint = f'https://login.microsoftonline.com/{tenantid}/oauth2/v2.0/token'

    # Define the required parameters for the token endpoint
    data = {
        'client_id': clientid,
        'client_secret': clientsecret,
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials'
    }
    # Make a request to the token endpoint to obtain an access token
    response = requests.post(token_endpoint, data=data)

    # 获得Access Token, Access Token的有效期为3600秒
    access_token = response.json()['access_token']
    print(access_token)

    #service Principal List All
    #url = f"https://graph.microsoft.com/v1.0/servicePrincipals"
    url = f"https://graph.microsoft.com/v1.0/servicePrincipals?$select=accountEnabled,id,appId,displayName,publisherName,servicePrincipalType"

    headers = {'Authorization': f'Bearer {access_token}',
               'ConsistencyLevel': 'eventual'}

    response = requests.get(url, headers = headers)
    response_data = response.json()
    print(response_data)
    


    #Service Principal Get By Object Id
    # objectid = "e1a0571c-4c3c-4014-a009-d2287dd24e67"
    # url = f"https://graph.microsoft.com/v1.0/servicePrincipals/{objectid}" 

    # response = requests.get(url, headers = headers)
    # response_data = response.json()
    # print(response_data)

if __name__ == "__main__":
    main()
