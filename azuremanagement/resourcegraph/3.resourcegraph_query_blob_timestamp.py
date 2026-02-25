import os
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest

'''
https://github.com/Azure-Samples/azure-samples-python-management/blob/main/samples/resourcegraph/resources_query.py
'''

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    clientcredential = ClientSecretCredential(tenantid, clientid, clientsecret)

    # Create SubscriptionClient to list all accessible subscriptions
    subscription_client = SubscriptionClient(clientcredential)
    subscriptions = [sub.subscription_id for sub in subscription_client.subscriptions.list()]

    # Create ResourceGraphClient
    resourcegraph_client = ResourceGraphClient(credential=clientcredential)

    # Basic query
    query = QueryRequest(
        query=f'''Resources
            | join kind=leftouter (ResourceContainers | where type=='microsoft.resources/subscriptions' | project subscriptionName=name, subscriptionId) on subscriptionId
            | where type == 'microsoft.compute/virtualmachines'
            | project subscriptionId,subscriptionName,resourceGroup,name,type,location,vmsize=properties.hardwareProfile.vmSize,
            osType=properties.storageProfile.osDisk.osType,
            publisher=properties.storageProfile.imageReference.publisher,offer=properties.storageProfile.imageReference.offer,
            sku=properties.storageProfile.imageReference.sku,
            osDisksizeInGB=properties.storageProfile.osDisk.diskSizeGB,
            dataDisksizeInGB=properties.storageProfile.dataDisks[0].diskSizeGB
            | sort by subscriptionId ''',
        subscriptions=subscriptions
    )

    query_response = resourcegraph_client.resources(query)
    print("Basic query object array:\n{}".format(query_response))

if __name__ == '__main__':
    main()
