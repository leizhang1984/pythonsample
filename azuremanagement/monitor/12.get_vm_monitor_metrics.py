import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.compute import ComputeManagementClient


def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')
    #订阅ID
    subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'
    #资源组名称
    rg_name = "aks-rg"
    #虚拟机名称
    vmname = "centos7.9"
    
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    compute_client = ComputeManagementClient(clientcredential, subscription_id)
    monitor_client = MonitorManagementClient(clientcredential, subscription_id)

    #获得虚拟机的信息
    vm = compute_client.virtual_machines.get(rg_name,vmname)
    resource_id = vm.id

    #统计的开始时间/统计的结束时间，是UTC时区
    timespan = '2025-04-11T08:38:00Z/2025-04-11T09:00:00Z'

    #虚拟机的指标值
    #https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-compute-virtualmachines-metrics


    #internal PT1H 代表每1小时,目前只支持1小时抽样间隔
    #internal PT1M 代表每1分钟
    #Percentage CPU	代表CPU利用率
    metric_result = monitor_client.metrics.list(resource_id,timespan,"PT1H","Percentage CPU","average",None,None,None)
  

    #Call REST API
    print(metric_result)


if __name__ == '__main__':
    main()


    '''
    下面是返回的Sample：
    {
  "cost": 21,
  "timespan": "2025-04-11T08:38:00Z/2025-04-11T09:00:00Z",
  "interval": "PT1M",
  "value": [
    {
      "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/aks-rg/providers/Microsoft.Compute/virtualMachines/centos7.9/providers/Microsoft.Insights/metrics/Percentage CPU",
      "type": "Microsoft.Insights/metrics",
      "name": {
        "value": "Percentage CPU",
        "localizedValue": "Percentage CPU"
      },
      "displayDescription": "The percentage of allocated compute units that are currently in use by the Virtual Machine(s)",
      "unit": "Percent",
      "timeseries": [
        {
          "metadatavalues": [],
          "data": [
            {
              "timeStamp": "2025-04-11T08:38:00Z",
              "average": 0.19
            },
            {
              "timeStamp": "2025-04-11T08:39:00Z",
              "average": 0.16
            },
            {
              "timeStamp": "2025-04-11T08:40:00Z",
              "average": 4.835
            },
            {
              "timeStamp": "2025-04-11T08:41:00Z",
              "average": 0.305
            },
            {
              "timeStamp": "2025-04-11T08:42:00Z",
              "average": 0.265
            },
            {
              "timeStamp": "2025-04-11T08:43:00Z",
              "average": 0.265
            },
            {
              "timeStamp": "2025-04-11T08:44:00Z",
              "average": 0.26
            },
            {
              "timeStamp": "2025-04-11T08:45:00Z",
              "average": 0.265
            },
            {
              "timeStamp": "2025-04-11T08:46:00Z",
              "average": 0.265
            },
            {
              "timeStamp": "2025-04-11T08:47:00Z",
              "average": 0.25
            },
            {
              "timeStamp": "2025-04-11T08:48:00Z",
              "average": 0.245
            },
            {
              "timeStamp": "2025-04-11T08:49:00Z",
              "average": 0.25
            },
            {
              "timeStamp": "2025-04-11T08:50:00Z",
              "average": 0.25
            },
            {
              "timeStamp": "2025-04-11T08:51:00Z",
              "average": 0.275
            },
            {
              "timeStamp": "2025-04-11T08:52:00Z",
              "average": 0.245
            },
            {
              "timeStamp": "2025-04-11T08:53:00Z",
              "average": 3.29
            },
            {
              "timeStamp": "2025-04-11T08:54:00Z",
              "average": 0.245
            },
            {
              "timeStamp": "2025-04-11T08:55:00Z",
              "average": 0.265
            },
            {
              "timeStamp": "2025-04-11T08:56:00Z",
              "average": 0.245
            },
            {
              "timeStamp": "2025-04-11T08:57:00Z",
              "average": 0.235
            },
            {
              "timeStamp": "2025-04-11T08:58:00Z",
              "average": 0.24
            },
            {
              "timeStamp": "2025-04-11T08:59:00Z",
              "average": 0.245
            }
          ]
        }
      ],
      "errorCode": "Success"
    }
  ],
  "namespace": "Microsoft.Compute/virtualMachines",
  "resourceregion": "germanywestcentral"
}
    '''