import os
import asyncio

from azure.identity import DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.identity import ClientSecretCredential
#pip install msgraph-sdk
from msgraph import GraphServiceClient

tenantid = os.environ.get('msdn_tenantid')
clientid = os.environ.get('msdn_clientid')
clientsecret = os.environ.get('msdn_clientsecret')

#订阅ID
sub_id = "b5aa1700-1510-4f35-b134-fe9c7c695df1"

#Management API
client_credential = ClientSecretCredential(tenantid,clientid,clientsecret)
authorization_client  = AuthorizationManagementClient(client_credential, sub_id)

#Graph API
# Create a credential object. Used to authenticate requests
### https://github.com/microsoftgraph/msgraph-sdk-python/blob/main/docs/users_samples.md
# Create a credential object. Used to authenticate requests

scopes = ['https://graph.microsoft.com/.default']
graph_service_client = GraphServiceClient(client_credential, scopes)


'''
https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/authorization/azure-mgmt-authorization/generated_samples/role_assignments_list_for_resource_group.py
'''

scope = "/subscriptions/b5aa1700-1510-4f35-b134-fe9c7c695df1/resourceGroups/defaultrg"

role_assignment= authorization_client.role_assignments.list_for_scope(scope,None)

async def async_for():
    for ra in role_assignment:
        print(f"Role Definication ID: {ra.role_definition_id}, Role Assignment ID: {ra.id}, Role Type: {ra.principal_type}, Role Assignment Name: {ra.name}")


asyncio.run(async_for())