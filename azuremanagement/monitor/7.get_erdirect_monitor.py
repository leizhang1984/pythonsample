import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient


tenantid = os.environ.get('tenantid')
clientid = os.environ.get('clientid')
clientsecret = os.environ.get('clientsecret')

def main():
    sub_id = '074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb'

    #credentials = DefaultAzureCredential()
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    monitor_client = MonitorManagementClient(credential=clientcredential, subscription_id=sub_id)

    resource_uri = '/subscriptions/074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb/resourceGroups/defaultrg/providers/Microsoft.Storage/storageAccounts/loglogstash/blobServices/default'

    timespan = '2022-12-25T05:38:44Z/2022-12-26T06:38:44Z'
    metricnamespace = 'Microsoft.Storage/storageAccounts"'


    result = monitor_client.metrics.list(
        resource_uri,
        # timespan="2022-12-14T05:38:44Z/2022-12-14T06:38:44Z",
        timespan,
        # metricnamespace="Microsoft.Storage/storageAccounts",
        metricnamespace,
        # filter="dim eq 'AccountResourceId'",
        filter="dim eq 'type'",
        top=1,
        orderby="Average asc",
        aggregation="Average,count", interval="PT1H"
    )
    print(result)

if __name__ == '__main__':
    main()