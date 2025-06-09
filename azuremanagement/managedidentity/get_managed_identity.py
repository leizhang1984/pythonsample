import os
from datetime import timedelta

#pip3 install azure-kusto-data
from azure.identity import ClientSecretCredential
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import *
from azure.mgmt.resource import SubscriptionClient

'''
https://github.com/Azure-Samples/azure-samples-python-management/blob/main/samples/resourcegraph/resources_query.py

nginxvm-01, nginxvm-02, nginxvm-03
'''

def query_mi_objectid(mi_objectid):

    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    subscription_client = SubscriptionClient(clientcredential)

    subscription_ids = [sub.subscription_id for sub in subscription_client.subscriptions.list()]
    
     # Create client
    # For other authentication approaches, please see: https://pypi.org/project/azure-identity/
    resourcegraph_client = ResourceGraphClient(
        credential = clientcredential
    )
    
    # 查询1
    # Managed Identity的所有属性
    query_mi = QueryRequest(
        query=f'''resources
        | where ["type"] == 'microsoft.managedidentity/userassignedidentities'
        | extend principalid= properties.principalId
        | where principalid == '{mi_objectid}'
        | project subscriptionId,resourceGroup, mi_name=name, location, principalid ''',
        subscriptions=subscription_ids
    )
    query_response = resourcegraph_client.resources(query_mi)
    
    # 结果1：
    # 查询Managed Identity的结果
    # 包含 subscriptionId
    # resourceGroup
    # mi_name
    # location
    # principalid
    if query_response.total_records > 0:
        for result in query_response.data:
            print("Result:")
            for key, value in result.items():
                print(f"  {key}: {value}")
    else:
        print("No results found.")


    # 查询2
    # 查询与上面的Managed Identity相关联的资源
    query_resources = QueryRequest(
        query=f'''resources
      | extend userAssignedIdentities= identity.userAssignedIdentities
      | where isnotempty(userAssignedIdentities)
      | where userAssignedIdentities contains '{mi_objectid}'
      | project subscriptionId,resourceGroup, resource_name=name, location, id''',
        subscriptions=subscription_ids
    )
    query_response = resourcegraph_client.resources(query_resources)

    # 结果2
    # 查询Managed Identity 相关联的资源
    if query_response.total_records > 0:
        for result in query_response.data:
            print("Result:")
            for key, value in result.items():
                print(f"  {key}: {value}")
    else:
        print("No results found.")

if __name__ == '__main__':
    mi_objectid = 'dace0dd5-d622-448d-ac4f-4ee1a0716af9'
    query_mi_objectid(mi_objectid)