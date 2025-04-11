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

    #Percentage CPU	                代表CPU利用率
    #Available Memory Percentage    代表可用内存百分比
    #Network In Total               代表入向流量
    #Network Out Total              代表出向流量
    metric_name = "Percentage CPU,Available Memory Percentage,Network In Total,Network Out Total"
    aggregation = "average,total"

    metric_result = monitor_client.metrics.list(resource_id,timespan,"PT1H",metric_name,aggregation,None,None,None)
  

    #Call REST API
    print(metric_result)


if __name__ == '__main__':
    main()


    '''
   {
    "cost": 44,
    "timespan": "2025-04-11T08:38:00Z/2025-04-11T08:50:00Z",
    "interval": "PT1M",
    "value": [
        {
            "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/aks-rg/providers/Microsoft.Compute/virtualMachines/centos7.9/providers/Microsoft.Insights/metrics/Network In Total",
            "type": "Microsoft.Insights/metrics",
            "name": {
                "value": "Network In Total",
                "localizedValue": "Network In Total"
            },
            "displayDescription": "The number of bytes received on all network interfaces by the Virtual Machine(s) (Incoming Traffic)",
            "unit": "Bytes",
            "timeseries": [
                {
                    "metadatavalues": [],
                    "data": [
                        {
                            "timeStamp": "2025-04-11T08:38:00Z",
                            "total": 0
                        },
                        {
                            "timeStamp": "2025-04-11T08:39:00Z",
                            "total": 360
                        },
                        {
                            "timeStamp": "2025-04-11T08:40:00Z",
                            "total": 1134093
                        },
                        {
                            "timeStamp": "2025-04-11T08:41:00Z",
                            "total": 43516
                        },
                        {
                            "timeStamp": "2025-04-11T08:42:00Z",
                            "total": 43333
                        },
                        {
                            "timeStamp": "2025-04-11T08:43:00Z",
                            "total": 43379
                        },
                        {
                            "timeStamp": "2025-04-11T08:44:00Z",
                            "total": 43313
                        },
                        {
                            "timeStamp": "2025-04-11T08:45:00Z",
                            "total": 43812
                        },
                        {
                            "timeStamp": "2025-04-11T08:46:00Z",
                            "total": 43313
                        },
                        {
                            "timeStamp": "2025-04-11T08:47:00Z",
                            "total": 43463
                        },
                        {
                            "timeStamp": "2025-04-11T08:48:00Z",
                            "total": 43463
                        },
                        {
                            "timeStamp": "2025-04-11T08:49:00Z",
                            "total": 43247
                        }
                    ]
                }
            ],
            "errorCode": "Success"
        },
        {
            "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/aks-rg/providers/Microsoft.Compute/virtualMachines/centos7.9/providers/Microsoft.Insights/metrics/Network Out Total",
            "type": "Microsoft.Insights/metrics",
            "name": {
                "value": "Network Out Total",
                "localizedValue": "Network Out Total"
            },
            "displayDescription": "The number of bytes out on all network interfaces by the Virtual Machine(s) (Outgoing Traffic)",
            "unit": "Bytes",
            "timeseries": [
                {
                    "metadatavalues": [],
                    "data": [
                        {
                            "timeStamp": "2025-04-11T08:38:00Z",
                            "total": 0
                        },
                        {
                            "timeStamp": "2025-04-11T08:39:00Z",
                            "total": 420
                        },
                        {
                            "timeStamp": "2025-04-11T08:40:00Z",
                            "total": 384388
                        },
                        {
                            "timeStamp": "2025-04-11T08:41:00Z",
                            "total": 341381
                        },
                        {
                            "timeStamp": "2025-04-11T08:42:00Z",
                            "total": 317909
                        },
                        {
                            "timeStamp": "2025-04-11T08:43:00Z",
                            "total": 317849
                        },
                        {
                            "timeStamp": "2025-04-11T08:44:00Z",
                            "total": 317849
                        },
                        {
                            "timeStamp": "2025-04-11T08:45:00Z",
                            "total": 340999
                        },
                        {
                            "timeStamp": "2025-04-11T08:46:00Z",
                            "total": 317915
                        },
                        {
                            "timeStamp": "2025-04-11T08:47:00Z",
                            "total": 317669
                        },
                        {
                            "timeStamp": "2025-04-11T08:48:00Z",
                            "total": 317669
                        },
                        {
                            "timeStamp": "2025-04-11T08:49:00Z",
                            "total": 317849
                        }
                    ]
                }
            ],
            "errorCode": "Success"
        },
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
                        }
                    ]
                }
            ],
            "errorCode": "Success"
        },
        {
            "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/aks-rg/providers/Microsoft.Compute/virtualMachines/centos7.9/providers/Microsoft.Insights/metrics/Available Memory Percentage",
            "type": "Microsoft.Insights/metrics",
            "name": {
                "value": "Available Memory Percentage",
                "localizedValue": "Available Memory Percentage (Preview)"
            },
            "displayDescription": "Amount of physical memory, in percentage, immediately available for allocation to a process or for system use in the Virtual Machine",
            "unit": "Percent",
            "timeseries": [
                {
                    "metadatavalues": [],
                    "data": [
                        {
                            "timeStamp": "2025-04-11T08:38:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2025-04-11T08:39:00Z",
                            "average": 89
                        },
                        {
                            "timeStamp": "2025-04-11T08:40:00Z",
                            "average": 89
                        },
                        {
                            "timeStamp": "2025-04-11T08:41:00Z",
                            "average": 89
                        },
                        {
                            "timeStamp": "2025-04-11T08:42:00Z",
                            "average": 89
                        },
                        {
                            "timeStamp": "2025-04-11T08:43:00Z",
                            "average": 89
                        },
                        {
                            "timeStamp": "2025-04-11T08:44:00Z",
                            "average": 89
                        },
                        {
                            "timeStamp": "2025-04-11T08:45:00Z",
                            "average": 89
                        },
                        {
                            "timeStamp": "2025-04-11T08:46:00Z",
                            "average": 89
                        },
                        {
                            "timeStamp": "2025-04-11T08:47:00Z",
                            "average": 89
                        },
                        {
                            "timeStamp": "2025-04-11T08:48:00Z",
                            "average": 89
                        },
                        {
                            "timeStamp": "2025-04-11T08:49:00Z",
                            "average": 89
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