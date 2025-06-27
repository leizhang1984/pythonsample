import os
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient, ResourceManagementClient
from msrestazure.azure_configuration import AzureConfiguration

def main():
    # 替换为你的服务主体信息
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')


    # 创建服务主体凭据
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)


    # 创建订阅客户端
    subscription_client = SubscriptionClient(clientcredential)

    # 获取所有订阅
    subscriptions = subscription_client.subscriptions.list()

    # 遍历每个订阅
    for subscription in subscriptions:
        subscription_id = subscription.subscription_id
        print(f"Subscription ID: {subscription_id}")
        print(f"Subscription Name: {subscription.display_name}")
        
        # 指定你需要的 API 版本
        api_version = '2021-04-01'  # 指定你需要的 API 版本

        # 创建资源管理客户端
        resource_client = ResourceManagementClient(clientcredential, subscription_id, api_version)

        # 列出该订阅中的所有资源及其标签
        for resource in resource_client.resources.list():
            print(f"  Resource ID: {resource.id}")
            print(f"  Resource Name: {resource.name}")
            print(f"  Resource Type: {resource.type}")
            print("  Tags:")
            if resource.tags:
                for tag_name, tag_value in resource.tags.items():
                    print(f"    {tag_name}: {tag_value}")
            else:
                print("    No tags")
            print("\n")
if __name__ == "__main__":
    main()