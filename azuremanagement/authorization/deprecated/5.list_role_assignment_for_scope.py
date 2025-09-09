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
credential = ClientSecretCredential(tenantid,clientid,clientsecret)
authorization_client  = AuthorizationManagementClient(
    credential = credential,
    subscription_id = sub_id
)

#Graph API
# Create a credential object. Used to authenticate requests
### https://github.com/microsoftgraph/msgraph-sdk-python/blob/main/docs/users_samples.md
# Create a credential object. Used to authenticate requests

scopes = ['https://graph.microsoft.com/.default']
graph_service_client = GraphServiceClient(credentials=credential, scopes=scopes)


'''
https://learn.microsoft.com/zh-cn/python/api/azure-mgmt-authorization/azure.mgmt.authorization.v2022_04_01.operations.roleassignmentsoperations?view=azure-python#azure-mgmt-authorization-v2022-04-01-operations-roleassignmentsoperations-list-for-scope
'''

scope = "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/lab-rg/providers/Microsoft.Storage/storageAccounts/leilabstorage01"

role_assignment= authorization_client.role_assignments.list_for_scope(scope,None)

async def async_for():
    for ra in role_assignment:
        print(ra.role_definition_id, ra.id, ra.principal_type, ra.name)

'''

'''
scope = "/subscriptions/b5aa1700-1510-4f35-b134-fe9c7c695df1/resourceGroups/LeiCloudShell/providers/Microsoft.Storage/storageAccounts/leimsdnstorage"
#filterstring = "principalID eq 'e1a0571c-4c3c-4014-a009-d2287dd24e67'"
filterstring = "assignedTo('22fd1119-5f07-4e98-86b2-6da94be0aeea')"

role_assignment= authorization_client.role_assignments.list_for_scope(scope,filterstring)

async def async_for():
     for ra in role_assignment:
         print(ra.role_definition_id, ra.id, ra.principal_type, ra.name)

asyncio.run(async_for())