import os
from datetime import timedelta

#pip3 install azure-kusto-data
from azure.identity import ClientSecretCredential
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import *

'''
https://github.com/Azure-Samples/azure-samples-python-management/blob/main/samples/resourcegraph/resources_query.py
'''

def main():

    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    subscriptionid = "166157a8-9ce9-400b-91c7-1d42482b83d6"

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    # Create client
    # For other authentication approaches, please see: https://pypi.org/project/azure-identity/
    resourcegraph_client = ResourceGraphClient(
        credential = clientcredential,
        subscription_id = subscriptionid
    )
    
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
            subscriptions=[subscriptionid]
        )
    
    query_response = resourcegraph_client.resources(query)
    print("Basic query object array:\n{}".format(query_response))

if __name__ == '__main__':
    main()