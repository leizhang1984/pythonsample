import os
import requests
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.authorization import AuthorizationManagementClient

# 查找分配的是一个用户，还是一个Application应用程序
def get_principal_name(access_token, principal_id):
    headers = {'Authorization': f'Bearer {access_token}', 'ConsistencyLevel': 'eventual'}

     # 尝试获取用户信息
     # 用户就是 类似 leizha@jt.com

     # 需要额外申请权限：https://learn.microsoft.com/en-us/graph/api/user-get?view=graph-rest-1.0&tabs=http
    user_url = f"https://graph.microsoft.com/v1.0/users/{principal_id}"
    response = requests.get(user_url, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data['displayName'], user_data['userPrincipalName'], user_data['id']

    # 尝试获取用户组信息

    #需要额外申请用户组的权限：https://learn.microsoft.com/en-us/graph/api/group-get?view=graph-rest-1.0&tabs=http
    group_url = f"https://graph.microsoft.com/v1.0/groups/{principal_id}"
    response = requests.get(group_url, headers=headers)
    if response.status_code == 200:
        group_data = response.json()
        return group_data['displayName'], None, group_data['id']

    # 尝试获取应用程序信息
    # 需要额外申请Application的权限：https://learn.microsoft.com/en-us/graph/api/application-get?view=graph-rest-1.0&tabs=http
    app_url = f"https://graph.microsoft.com/v1.0/applications/{principal_id}"
    response = requests.get(app_url, headers=headers)
    if response.status_code == 200:
        app_data = response.json()
        return app_data['displayName'], None, app_data['id']

    # 尝试获取Service Principal
    # 需要额外申请Service Principal的权限：https://learn.microsoft.com/en-us/graph/api/serviceprincipal-get?view=graph-rest-1.0&tabs=http
    sp_url = f"https://graph.microsoft.com/v1.0/servicePrincipals/{principal_id}"
    response = requests.get(sp_url, headers=headers)
    if response.status_code == 200:
        sp_data = response.json()
        return sp_data['displayName'], None, sp_data['id']

    return 'Unknown Principal', None, None

# 找到订阅分配的角色
def get_role_assignments(tenant_id, client_id, client_secret, subscription_id, access_token):
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    authorization_client = AuthorizationManagementClient(credential, subscription_id)
    role_assignments = authorization_client.role_assignments.list_for_subscription()

    for role_assignment in role_assignments:
        principal_id = role_assignment.principal_id
        role_definition_id = role_assignment.role_definition_id
        roleassignment_scope = role_assignment.scope

        # 获取用户名或应用程序名称
        displayname, user_principal_name, user_id = get_principal_name(access_token, principal_id)

        # 获取角色定义
        role_definition = authorization_client.role_definitions.get(
            scope=role_assignment.scope,
            role_definition_id=role_definition_id.split('/')[-1]
        )

        # 打印用户、角色和角色的具体内容
        print(f"Displayname : {displayname}")
        print(f"User Principal Name: {user_principal_name}")
        print(f"Scope: {roleassignment_scope}")
        print(f"Role Name: {role_definition.role_name}")
        print(f"Role Description: {role_definition.description}")

        # 打印角色权限的所有内容
        print("Role Permissions:")
        for permission in role_definition.permissions:
            print(f"  Actions: {permission.actions}")
            print(f"  NotActions: {permission.not_actions}")
            print(f"  DataActions: {permission.data_actions}")
            print(f"  NotDataActions: {permission.not_data_actions}")
        print("-" * 40)

def get_access_token(tenant_id, client_id, client_secret):
    token_endpoint = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials'
    }
    response = requests.post(token_endpoint, data=data)
    response.raise_for_status()  # 如果请求失败，则抛出异常
    return response.json()['access_token']

def main():
    # 替换为你的服务主体信息
    tenant_id = os.environ.get('msdn_tenantid')
    client_id = os.environ.get('msdn_clientid')
    client_secret = os.environ.get('msdn_clientsecret')

    # 获取一次 Access Token
    access_token = get_access_token(tenant_id, client_id, client_secret)

    # 创建服务主体凭据
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)

    # 创建订阅客户端
    subscription_client = SubscriptionClient(credential)

    # 获取所有订阅
    subscriptions = subscription_client.subscriptions.list()

    # 遍历每个订阅
    for subscription in subscriptions:
        subscription_id = subscription.subscription_id
        print(f"Subscription ID: {subscription_id}")

        # 获取并打印角色分配
        get_role_assignments(tenant_id, client_id, client_secret, subscription_id, access_token)

    print("Completed checking all subscriptions.")

if __name__ == "__main__":
    main()
