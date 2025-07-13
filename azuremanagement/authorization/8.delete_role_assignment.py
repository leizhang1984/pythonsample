import os
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.authorization import AuthorizationManagementClient

# 服务主体的凭据
tenant_id = os.environ.get('msdn_tenantid')
client_id = os.environ.get('msdn_clientid')
client_secret = os.environ.get('msdn_clientsecret')

# 使用服务主体进行身份验证
credential = ClientSecretCredential(tenant_id, client_id, client_secret)

# 创建订阅客户端
subscription_client = SubscriptionClient(credential)

# 获取所有订阅
subscriptions = subscription_client.subscriptions.list()

####################过滤条件####################
strfilterstring = "roleName eq 'Reader'"

# 遍历所有订阅
for subscription in subscriptions:
    subscription_id = subscription.subscription_id
    print(f"Processing subscription: {subscription_id}")

    # 创建授权管理客户端
    auth_client = AuthorizationManagementClient(credential, subscription_id)

    # 获取 Reader 角色定义的ID
    role_definitions = auth_client.role_definitions.list(scope='/subscriptions/' + subscription_id, filter=strfilterstring)
    for role_definition in role_definitions:
        reader_role_definition_id = role_definition.id
        break

    if reader_role_definition_id is None:
        print(f"Reader role definition not found in subscription: {subscription_id}")
        continue

    # 使用过滤器获取所有 Reader 角色分配
    filter_str = f"roleDefinitionId eq '{reader_role_definition_id}'"
    role_assignments = auth_client.role_assignments.list_for_subscription()

     # 遍历所有角色分配并过滤出 Reader 角色分配
    for role_assignment in role_assignments:
        if role_assignment.role_definition_id == reader_role_definition_id:
            print(f"Deleting Reader role assignment: {role_assignment.id}")
            auth_client.role_assignments.delete_by_id(role_assignment.id)

print("Completed processing all subscriptions.")
