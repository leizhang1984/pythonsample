import time,os,sys

from azure.identity import ClientSecretCredential
from azure.mgmt.quota import QuotaMgmtClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.machinelearningservices import AzureMachineLearningWorkspaces


'''
Azure Machine Learning
'''
def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    #Azure数据中心区域
    #location = "germanywestcentral"
    location = "swedencentral"

    #Azure订阅ID
    subscriptionid = "166157a8-9ce9-400b-91c7-1d42482b83d6"

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    quota_client = QuotaMgmtClient(clientcredential, subscriptionid)
    #compute_client = ComputeManagementClient(clientcredential, subscriptionid)
    ml_client = AzureMachineLearningWorkspaces(clientcredential, subscriptionid)

    #获得当前所有Machine Learning的Usage
    usages = ml_client.usages.list(location)

    #获得当前所有Machine Learning的quota
    print("Azure Machine Learning Usages:")
    for usage in usages:
        print(f"Name: {usage.name.value}, current_value: {usage.current_value}, limit: {usage.limit}")

    #quota_sku, limit_value, quota_new_limit 都是从上面的循环中获得
    #我们取其中一个quota
    quota_sku = "standardDv3Family"
    limit_value = 100
    quota_new_limit = 110
    
    #判断一下
    if(quota_new_limit < limit_value):
        sys.exit(1)

    #需要申请新的Quota
    result = quota_client.quota.begin_create_or_update(
    resource_name=quota_sku,
    scope=f"subscriptions/{subscriptionid}/providers/Microsoft.MachineLearningServices/locations/{location}",
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
