import os
import asyncio
from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.resource import SubscriptionClient

# 获取环境变量中的凭据
tenantid = os.environ.get('nonprod_tenantid')
clientid = os.environ.get('nonprod_clientid')
clientsecret = os.environ.get('nonprod_clientsecret')
# 创建凭据对象
client_credential = ClientSecretCredential(tenantid, clientid, clientsecret)

# 获取所有订阅
subscription_client = SubscriptionClient(client_credential)
subscriptions = subscription_client.subscriptions.list()

####################过滤条件####################
strfilterstring = "type eq 'CustomRole'"


# 遍历所有订阅并获取角色定义
async def get_role_definitions():
    for subscription in subscriptions:
        sub_id = subscription.subscription_id
        print(f"Processing subscription: {sub_id}")

        # 创建授权管理客户端
        authorization_client = AuthorizationManagementClient(
            credential=client_credential,
            subscription_id=sub_id
        )

        # 列出角色定义
        role_definitions = authorization_client.role_definitions.list(scope='/subscriptions/' + sub_id, filter=strfilterstring)
        for role_definition in role_definitions:
            print(f"Role Name: {role_definition.role_name}, Role Type: {role_definition.role_type}, Role Description: {role_definition.description}")

# 运行异步函数
asyncio.run(get_role_definitions())
