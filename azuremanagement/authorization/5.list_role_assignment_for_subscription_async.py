import os
import asyncio
from azure.identity import ClientSecretCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from msgraph import GraphServiceClient
from azure.mgmt.resource import SubscriptionClient

async def get_principal_info(principal_type, principal):
    if principal_type == "User":
        # 尝试获取用户信息
        # 用户就是 类似 leizha@jt.com

        # 需要额外申请权限：https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0&tabs=http
        return principal.display_name, principal.user_principal_name, principal.id
    
    elif principal_type == "Group":
        # 尝试获取用户组信息
        #需要额外申请用户组的权限：https://learn.microsoft.com/en-us/graph/api/group-get?view=graph-rest-1.0&tabs=http
        return principal.display_name, "None", principal.id
    
    elif principal_type == "Application":
        # 尝试获取应用程序信息
        # 需要额外申请Application的权限：https://learn.microsoft.com/en-us/graph/api/application-get?view=graph-rest-1.0&tabs=http
        return principal.display_name, "None", principal.id
    
    elif principal_type == "ServicePrincipal":
        # 尝试获取Service Principal
        # 需要额外申请Service Principal的权限：https://learn.microsoft.com/en-us/graph/api/serviceprincipal-get?view=graph-rest-1.0&tabs=http
        return principal.display_name, "None", principal.id

async def async_for(subscriptions, client_credential, graph_service_client):
    for subscription in subscriptions:
        sub_id = subscription.subscription_id
        print(f"Processing subscription: {sub_id}")
        
        authorization_client = AuthorizationManagementClient(client_credential, sub_id)

        # 找到之前分配的权限
        role_assignments = authorization_client.role_assignments.list_for_subscription()

        for role_assignment in role_assignments:
            print(f"Principal Type: {role_assignment.principal_type}")
            try:
                principal = None
                if role_assignment.principal_type == "User":
                    principal = await graph_service_client.users.by_user_id(role_assignment.principal_id).get()
                elif role_assignment.principal_type == "Group":
                    principal = await graph_service_client.groups.by_group_id(role_assignment.principal_id).get()
                elif role_assignment.principal_type == "Application":
                    principal = await graph_service_client.applications.by_application_id(role_assignment.principal_id).get()
                elif role_assignment.principal_type == "ServicePrincipal":
                    principal = await graph_service_client.service_principals.by_service_principal_id(role_assignment.principal_id).get()
               
                if principal:
                    display_name, principal_name, principal_id = await get_principal_info(role_assignment.principal_type, principal)
                    print(f"Display Name: {display_name}")
                    print(f"Principal Name: {principal_name}")
                    print(f"ID: {principal_id}")
                    print(f"Scope: {role_assignment.scope}")

                # 获取 role_definition
                role_definition_id = role_assignment.role_definition_id
                role_definition = authorization_client.role_definitions.get(
                    scope=role_assignment.scope,
                    role_definition_id=role_definition_id.split('/')[-1]
                )
        
                print(f"Role Definition Name: {role_definition.role_name}")
                print(f"Role Definition Description: {role_definition.description}")

                # 打印角色权限的所有内容
                print("Role Permissions:")
                for permission in role_definition.permissions:
                    print(f"  Actions: {permission.actions}")
                    print(f"  NotActions: {permission.not_actions}")
                    print(f"  DataActions: {permission.data_actions}")
                    print(f"  NotDataActions: {permission.not_data_actions}")
                print("-" * 40)

            except Exception as e:
                print(f"Error retrieving {role_assignment.principal_type}: {e}")
                print("-" * 40)

def main():
    # 获取环境变量中的凭据
    tenantid = os.environ.get('msdn_tenantid')
    clientid = os.environ.get('msdn_clientid')
    clientsecret = os.environ.get('msdn_clientsecret')

    # 创建凭据对象
    client_credential = ClientSecretCredential(tenantid, clientid, clientsecret)

    # 获取所有订阅
    subscription_client = SubscriptionClient(client_credential)
    subscriptions = subscription_client.subscriptions.list()

    # Graph API
    # Create a credential object. Used to authenticate requests
    scopes = ['https://graph.microsoft.com/.default']
    graph_service_client = GraphServiceClient(client_credential, scopes=scopes)

    # 运行异步函数
    asyncio.run(async_for(subscriptions, client_credential, graph_service_client))

if __name__ == "__main__":
    main()
