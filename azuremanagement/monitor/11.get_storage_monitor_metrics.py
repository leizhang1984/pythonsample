import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.storage import StorageManagementClient


def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')
    #订阅ID
    subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'
    #资源组名称
    rg_name = "test-rg"
    #存储账户名称
    storageaccount_name = "leiteststorage000"
    
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    storage_client = StorageManagementClient(clientcredential, subscription_id)
    monitor_client = MonitorManagementClient(clientcredential, subscription_id)

    #获得Storage Account信息
    storage = storage_client.storage_accounts.get_properties(rg_name,storageaccount_name)
    resource_id = storage.id

    #统计的开始时间/统计的结束时间，是UTC时区
    timespan = '2025-03-24T07:00:00Z/2025-03-25T07:41:00Z'
    #metricnamespace这个不用改
    metricnamespace = 'Microsoft.Storage/storageAccounts'

    #Support Metric
    #https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-storage-storageaccounts-metrics


    #internal PT1H 代表每1小时,目前只支持1小时抽样间隔
    #internal PT1M 代表每1分钟
    #返回的结果是B，需要自己换算成MB
    metric_result = monitor_client.metrics.list(resource_id,timespan,"PT1H","UsedCapacity","average",None,None,None)
  

    #Call REST API
    print(metric_result)


if __name__ == '__main__':
    main()


    '''
    下面是返回的Sample：
    {
  "cost": 1480,
  "timespan": "2025-03-24T07:00:00Z/2025-03-25T07:41:00Z",
  "interval": "PT1H",
  "value": [
    {
      "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/test-rg/providers/Microsoft.Storage/storageAccounts/leiteststorage000/providers/Microsoft.Insights/metrics/UsedCapacity",
      "type": "Microsoft.Insights/metrics",
      "name": {
        "value": "UsedCapacity",
        "localizedValue": "Used capacity"
      },
      "displayDescription": "The amount of storage used by the storage account. For standard storage accounts, it's the sum of capacity used by blob, table, file, and queue. For premium storage accounts and Blob storage accounts, it is the same as BlobCapacity or FileCapacity.",
      "unit": "Bytes",
      "timeseries": [
        {
          "metadatavalues": [],
          "data": [
            {
              "timeStamp": "2025-03-24T07:00:00Z",
              "average": 15358376
            },
            {
              "timeStamp": "2025-03-24T08:00:00Z",
              "average": 15358376
            },
            {
              "timeStamp": "2025-03-24T09:00:00Z",
              "average": 15358376
            },
            {
              "timeStamp": "2025-03-24T10:00:00Z",
              "average": 15358376
            },
            {
              "timeStamp": "2025-03-24T11:00:00Z",
              "average": 15358376
            },
            {
              "timeStamp": "2025-03-24T12:00:00Z",
              "average": 15358376
            },
            {
              "timeStamp": "2025-03-24T13:00:00Z",
              "average": 15358376
            },
            {
              "timeStamp": "2025-03-24T14:00:00Z",
              "average": 15358376
            },
            {
              "timeStamp": "2025-03-24T15:00:00Z",
              "average": 15358376
            },
            {
              "timeStamp": "2025-03-24T16:00:00Z",
              "average": 15358376
            },
            {
              "timeStamp": "2025-03-24T17:00:00Z",
              "average": 15358376
            },
            {
              "timeStamp": "2025-03-24T18:00:00Z",
              "average": 15339660
            },
            {
              "timeStamp": "2025-03-24T19:00:00Z",
              "average": 15339660
            },
            {
              "timeStamp": "2025-03-24T20:00:00Z",
              "average": 15339660
            },
            {
              "timeStamp": "2025-03-24T21:00:00Z",
              "average": 15339660
            },
            {
              "timeStamp": "2025-03-24T22:00:00Z",
              "average": 15339660
            },
            {
              "timeStamp": "2025-03-24T23:00:00Z",
              "average": 15339660
            },
            {
              "timeStamp": "2025-03-25T00:00:00Z",
              "average": 15339660
            },
            {
              "timeStamp": "2025-03-25T01:00:00Z",
              "average": 15339660
            },
            {
              "timeStamp": "2025-03-25T02:00:00Z",
              "average": 15339660
            },
            {
              "timeStamp": "2025-03-25T03:00:00Z",
              "average": 15339660
            },
            {
              "timeStamp": "2025-03-25T04:00:00Z",
              "average": 15339660
            },
            {
              "timeStamp": "2025-03-25T05:00:00Z",
              "average": 15339660
            },
            {
              "timeStamp": "2025-03-25T06:00:00Z",
              "average": 15339660
            },
            {
              "timeStamp": "2025-03-25T07:00:00Z",
              "average": 15339660
            }
          ]
        }
      ],
      "errorCode": "Success"
    }
  ],
  "namespace": "Microsoft.Storage/storageAccounts",
  "resourceregion": "germanywestcentral"
}
    '''