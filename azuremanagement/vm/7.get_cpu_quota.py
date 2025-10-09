import os
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import SubscriptionClient

def main():
    # 从环境变量中获取服务主体的凭据
    tenant_id = os.getenv('msdn_tenantid')
    client_id = os.getenv('msdn_clientid')
    client_secret = os.getenv('msdn_clientsecret')

    if not tenant_id or not client_id or not client_secret:
        raise ValueError("请确保已设置环境变量 AZURE_TENANT_ID, AZURE_CLIENT_ID 和 AZURE_CLIENT_SECRET")

    # 创建服务主体的凭据对象
    credential = ClientSecretCredential(
        tenant_id=tenant_id,
        client_id=client_id,
        client_secret=client_secret
    )

    # 创建订阅客户端
    subscription_client = SubscriptionClient(credential)

    # 获取所有订阅
    subscriptions = subscription_client.subscriptions.list()

    # 循环所有订阅
    for subscription in subscriptions:
        subscription_id = subscription.subscription_id
        print(f"Processing subscription: {subscription_id}")

        # 创建 ComputeManagementClient
        compute_client = ComputeManagementClient(credential, subscription_id)

        # 获取使用情况
        usage_list = compute_client.usage.list("westeurope")
        for usage in usage_list:
            print(usage.as_dict())

if __name__ == "__main__":
    main()
