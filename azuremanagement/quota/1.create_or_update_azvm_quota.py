import time,os,sys

from azure.identity import ClientSecretCredential
from azure.mgmt.quota import QuotaMgmtClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient

'''
Azure虚拟机的Quota
'''
def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    #Azure数据中心区域
    location = "germanywestcentral"
    #location = "swedencentral"

    #Azure订阅ID
    subscriptionid = "166157a8-9ce9-400b-91c7-1d42482b83d6"

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    quota_client = QuotaMgmtClient(clientcredential, subscriptionid)
    compute_client = ComputeManagementClient(clientcredential, subscriptionid)

    usages = compute_client.usage.list(location)


    #获得当前的所有虚拟机的quota
    print("Virtual Machine Quotas:")
    for usage in usages:
        print(f"Name: {usage.name.value}, Current Value: {usage.current_value}, Limit: {usage.limit}")
    
    #quota_sku, limit_value, quota_new_limit 都是从上面的循环中获得
    #我们取其中一个quota
    quota_sku = "standardDSv5Family"
    limit_value = 110
    quota_new_limit = 120
    
    #判断一下
    if(quota_new_limit < limit_value):
        sys.exit(1)

    #需要申请新的Quota
    result = quota_client.quota.begin_create_or_update(
    resource_name=quota_sku,
    scope=f"subscriptions/{subscriptionid}/providers/Microsoft.Compute/locations/{location}",
    create_quota_request={
        "properties": {
            "limit": {
                "limitObjectType": "LimitValue",
                "value": quota_new_limit,
            },
            "name": {"value": quota_sku},
        }
    },
    retry_total = 0
    ).result()

    print(result)


if __name__ == '__main__':
    main()
