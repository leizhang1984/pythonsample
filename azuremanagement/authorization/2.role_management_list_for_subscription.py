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


####################过滤条件####################
filterstring = "atScope()"
#filterstring = "principalID eq 'c21fc638-374c-4c63-8061-727a1c69e802'"
#filterstring = "assignedtp('{value}')"

'''
https://github.com/Azure-Samples/azure-samples-python-management/blob/main/samples/authorization/manage_role_management_policy.py
'''
####################找到之前分配的权限################
#role_assignment= authorization_client.role_assignments.list_for_subscription(filterstring,None)
role_assignment = authorization_client.role_assignments.list_for_subscription(None,None)

async def async_for():
    for ra in role_assignment:
        #ra.role_definition_id = role definition id
        #/subscriptions/b5aa1700-1510-4f35-b134-fe9c7c695df1/providers/Microsoft.Authorization/roleDefinitions/ba92f5b4-2d11-453d-a403-e96b0029c9fe
        
        #ra.id                 = role roleAssignments id
        # /subscriptions/b5aa1700-1510-4f35-b134-fe9c7c695df1/resourcegroups/test-rg/providers/Microsoft.Authorization/roleAssignments/c99a2fb0-81ec-495a-8b26-1ce87ab9307a

        #ra.principal_type     = pricniple type (User, Group, ServicePrincipal)

        #ra.name is Role Assignment GUID
        #c99a2fb0-81ec-495a-8b26-1ce87ab9307a

        print(ra.role_definition_id, ra.id, ra.principal_type, ra.name)

