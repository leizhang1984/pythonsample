import os
import asyncio
from azure.identity import DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.identity import ClientSecretCredential
#pip install msgraph-sdk
from msgraph import GraphServiceClient

tenantid = os.environ.get('tenantid')
clientid = os.environ.get('clientid')
clientsecret = os.environ.get('clientsecret')

#订阅ID
sub_id = "b5aa1700-1510-4f35-b134-fe9c7c695df1"

#Management API
clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
authorization_client  = AuthorizationManagementClient(
    credential = clientcredential,
    subscription_id = sub_id
)

#Graph API
# Create a credential object. Used to authenticate requests
### https://github.com/microsoftgraph/msgraph-sdk-python/blob/main/docs/users_samples.md
# Create a credential object. Used to authenticate requests

scopes = ['https://graph.microsoft.com/.default']
graph_service_client = GraphServiceClient(credentials=clientcredential, scopes=scopes)


####################过滤条件####################
filterstring = "atScope()"
#filterstring = "principalID eq 'c21fc638-374c-4c63-8061-727a1c69e802'"
#filterstring = "assignedtp('{value}')"

####################找到之前分配的权限################
role_assignment= authorization_client.role_assignments.list_for_subscription(filterstring,None)

async def async_for():
    for ra in role_assignment:
        #这个是Storage Blob Data Contributor值是：ba92f5b4-2d11-453d-a403-e96b0029c9fe
        #Owner的值是：8e3af657-a8ff-443c-a75c-2fe8c4bcb635
        roledefid = "/subscriptions/{subscriptionId}/providers/Microsoft.Authorization/roleDefinitions/8e3af657-a8ff-443c-a75c-2fe8c4bcb635".format(
        subscriptionId=sub_id
        )
        #用户
        if ra.role_definition_id == roledefid and ra.principal_type == "User":
            #这里只能拿到用户/用户组的objectid,然后通过object id拿到显示名称
            #必须用async，否则没办法取到值
            #async def get_user():
                user = await graph_service_client.users.by_user_id(ra.principal_id).get()
                if user:
                    print(user.display_name)
            #asyncio.run(get_user())
        #用户组
        if ra.role_definition_id == roledefid and ra.principal_type == "Group":
            #async def get_group():
                group = await graph_service_client.groups.by_group_id(ra.principal_id).get()
                if group:
                    print(group.display_name)
            #asyncio.run(get_group())
        #应用注册
        if ra.role_definition_id == roledefid and ra.principal_type == "ServicePrincipal":
            #async def get_sp():
                sp = await graph_service_client.service_principals.by_service_principal_id(ra.principal_id).get()
                if sp:
                    print(sp.display_name)
            #asyncio.run(get_sp())

asyncio.run(async_for())