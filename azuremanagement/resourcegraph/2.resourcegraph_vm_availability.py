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
        query=f'''healthresourcechanges 
            | where type =~ 'microsoft.resources/changes' 
            | where properties.targetResourceType =~ 'microsoft.resourcehealth/resourceannotations' 
            | extend Timestamp = todatetime(properties.changeAttributes.timestamp) 
            | where Timestamp > ago(1d) 
            | extend ResourceId = split(properties.targetResourceId, '/providers/Microsoft.ResourceHealth/resourceAnnotations/current')[0] 
            | where ResourceId !contains 'virtualMachineScaleSets'
            | extend Sub = split(ResourceId, '/')[2] | extend RG = split(ResourceId, '/')[4] 
            | extend VMName = tostring(split(ResourceId, '/')[8]) 
            | extend Context = properties['changes']['properties.context']['newValue'] 
            | extend Category = properties['changes']['properties.category']['newValue'] 
            | extend ImpactType = properties['changes']['properties.impactType']['newValue'] 
            | extend AnnotationName = split(properties['changes']['properties.annotationName']['newValue'], '//')[0] 
            | where AnnotationName in~ ('VirtualMachineHostCrashed', 'VirtualMachineHostRebootedForRepair', 'VirtualMachineMigrationInitiatedForRepair', 'VirtualMachineStorageOffline', 'VirtualMachinePossiblyDegradedDueToHardwareFailureWithRedeployDeadline', 'VirtualMachineMigrationScheduledForDegradedHardware', 'VirtualMachinePossiblyDegradedDueToHardwareFailure', 'VirtualMachineScheduledForServiceHealing', 'AccelnetUnhealthy', 'LiveMigrationSucceeded', 'LiveMigrationFailure', 'VirtualMachineMigrationInitiatedForPlannedMaintenance', 'VirtualMachineRebootInitiatedForPlannedMaintenance', 'VirtualMachinePlannedFreezeSucceeded', 'VirtualMachinePlannedFreezeFailed', 'VirtualMachineProvisioningTimedOut', 'VirtualMachineCrashed') 
            | extend Reason = properties['changes']['properties.reason']['newValue'] 
            | extend Summary = properties['changes']['properties.summary']['newValue'] 
            | join kind=leftouter (resources
            | where type == 'microsoft.network/networkinterfaces'
            | where isnotempty(properties.virtualMachine.id)
            | extend vmName = tostring(split(properties.virtualMachine.id, '/')[-1])
            | mv-expand ipConfig = properties.ipConfigurations
            | summarize privateIPs = make_list(ipConfig.properties.privateIPAddress) by vmName
            ) on $left.VMName == $right.vmName
            | project Timestamp, ResourceId, Sub, RG, VMName, Context, Category, ImpactType, AnnotationName, Reason, Summary, privateIPs 
            | order by Timestamp asc''',
        subscriptions=subscriptions
    )

    query_response = resourcegraph_client.resources(query)
    print("vm availaibiltiy result:\n{}".format(query_response))

if __name__ == '__main__':
    main()
