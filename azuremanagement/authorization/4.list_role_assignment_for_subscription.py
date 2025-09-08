from azure.identity import ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.authorization import AuthorizationManagementClient
from msgraph import GraphServiceClient
import os,requests

#查找分配的是一个用户，还是一个Application应用程序
def get_principal_name(tenant_id,client_id,client_secret, principal_id):
    # 1.先获得Access Token
    token_endpoint = f'https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token'

    # Define the required parameters for the token endpoint
    data = {
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials'
    }
    # Make a request to the token endpoint to obtain an access token
    response = requests.post(token_endpoint, data=data)

    # 获得Access Token, Access Token的有效期为3600秒
    access_token = response.json()['access_token']

    url = f"https://graph.microsoft.com/v1.0/users/{principal_id}"

    headers = {'Authorization': f'Bearer {access_token}',
               'ConsistencyLevel': 'eventual'}

     # 尝试获取用户信息
     # 用户就是 类似 leizha@jt.com
    user_url = f"https://graph.microsoft.com/v1.0/users/{principal_id}"
    response = requests.get(user_url, headers=headers)
    if response.status_code == 200:
        user_data = response.json()
        return user_data['displayName'], user_data['userPrincipalName'], user_data['id']

    # 尝试获取用户组信息
    group_url = f"https://graph.microsoft.com/v1.0/groups/{principal_id}"
    response = requests.get(group_url, headers=headers)
    if response.status_code == 200:
        group_data = response.json()
        return group_data['displayName'], None, group_data['id']

    # 尝试获取应用程序信息
    app_url = f"https://graph.microsoft.com/v1.0/applications/{principal_id}"
    response = requests.get(app_url, headers=headers)
    if response.status_code == 200:
        app_data = response.json()
        return app_data['displayName'], None, app_data['id']
    
    # 尝试获取Service Principal
    app_url = f"https://graph.microsoft.com/v1.0/servicePrincipals/{principal_id}"
    response = requests.get(app_url, headers=headers)
    if response.status_code == 200:
        app_data = response.json()
        return app_data['displayName'], None, app_data['id']

    return 'Unknown Principal', None, None

# 找到订阅分配的角色
def get_role_assignments(tenant_id,client_id,client_secret, subscription_id):
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    authorization_client = AuthorizationManagementClient(credential, subscription_id)
    role_assignments = authorization_client.role_assignments.list_for_subscription(None,None)
    
    for role_assignment in role_assignments:
        principal_id = role_assignment.principal_id
        role_definition_id = role_assignment.role_definition_id
        #生效范围
        roleassignment_scope = role_assignment.scope
        
        # 获取用户名或应用程序名称
        displayname, user_principal_name, user_id = get_principal_name(tenant_id, client_id, client_secret, principal_id)
        
        # 获取角色定义
        role_definition = authorization_client.role_definitions.get(
            scope=role_assignment.scope,
            role_definition_id=role_definition_id.split('/')[-1]
        )
        
        # 打印用户、角色和角色的具体内容
        print(f"Displayname : {displayname}")
        print(f"User Principal Name: {user_principal_name}")

        #生效范围
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

def main():
    # 替换为你的服务主体信息
    tenant_id = os.environ.get('msdn_tenantid')
    client_id = os.environ.get('msdn_clientid')
    client_secret = os.environ.get('msdn_clientsecret')

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
        get_role_assignments(tenant_id,client_id,client_secret, subscription_id)

    print("Completed checking all subscriptions.")

if __name__ == "__main__":
    main()
