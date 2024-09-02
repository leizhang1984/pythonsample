import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.network import NetworkManagementClient


def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'
    rg_name = "FW-Hybrid-Test"
    applicationgateway_name = "leiappgw01"
    
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    network_client = NetworkManagementClient(credential=clientcredential, subscription_id = subscription_id)
    monitor_client = MonitorManagementClient(credential=clientcredential, subscription_id = subscription_id)

    #获得负载均衡器信息
    application_gateway = network_client.application_gateways.get(rg_name,applicationgateway_name)
    resource_id = application_gateway.id
    
    #开始时间和结束时间
    timespan = '2024-08-27T01:40:00Z/2024-08-28T07:41:00Z'
    metricnamespace = 'Microsoft.Network/loadBalancers'

    #Support Metric
    #https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-network-applicationgateways-metrics


    #拿到负载均衡器后端的ip地址，具体步骤略。
    #我这里后端的ip分别是：10.99.76.10 和10.99.76.14

    #internal PT1H 代表每1小时
    #BackendResponseStatus 代表后端服务是否健康
    #
    result = monitor_client.metrics.list(resource_id,timespan,"PT1H","CapacityUnits","Average",None,None, None)
    print(result)
    
    result = monitor_client.metrics.list(resource_id,timespan,"PT1H","ComputeUnits","Average",None,None, None)
    print(result)



if __name__ == '__main__':
    main()

'''
下面是capacity Unit的返回值
{
    "cost": 1739,
    "timespan": "2024-08-27T01:27:00Z/2024-08-28T06:27:00Z",
    "interval": "PT1H",
    "value": [
        {
            "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/FW-Hybrid-Test/providers/Microsoft.Network/applicationGateways/leiappgw01/providers/Microsoft.Insights/metrics/CapacityUnits",
            "type": "Microsoft.Insights/metrics",
            "name": {
                "value": "CapacityUnits",
                "localizedValue": "Current Capacity Units"
            },
            "displayDescription": "Capacity Units consumed",
            "unit": "Count",
            "timeseries": [
                {
                    "metadatavalues": [],
                    "data": [
                        {
                            "timeStamp": "2024-08-27T01:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T02:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T03:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T04:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T05:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T06:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T07:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T08:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T09:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T10:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T11:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T12:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T13:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T14:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T15:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T16:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T17:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T18:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T19:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T20:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T21:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T22:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T23:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-28T00:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-28T01:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-28T02:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-28T03:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-28T04:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-28T05:27:00Z",
                            "average": 0
                        }
                    ]
                }
            ],
            "errorCode": "Success"
        }
    ],
    "namespace": "Microsoft.Network/applicationGateways",
    "resourceregion": "japaneast"
}

'''



'''
{
    "cost": 1739,
    "timespan": "2024-08-27T01:27:00Z/2024-08-28T06:27:00Z",
    "interval": "PT1H",
    "value": [
        {
            "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/FW-Hybrid-Test/providers/Microsoft.Network/applicationGateways/leiappgw01/providers/Microsoft.Insights/metrics/ComputeUnits",
            "type": "Microsoft.Insights/metrics",
            "name": {
                "value": "ComputeUnits",
                "localizedValue": "Current Compute Units"
            },
            "displayDescription": "Compute Units consumed",
            "unit": "Count",
            "timeseries": [
                {
                    "metadatavalues": [],
                    "data": [
                        {
                            "timeStamp": "2024-08-27T01:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T02:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T03:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T04:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T05:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T06:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T07:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T08:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T09:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T10:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T11:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T12:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T13:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T14:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T15:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T16:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T17:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T18:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T19:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T20:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T21:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T22:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-27T23:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-28T00:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-28T01:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-28T02:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-28T03:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-28T04:27:00Z",
                            "average": 0
                        },
                        {
                            "timeStamp": "2024-08-28T05:27:00Z",
                            "average": 0
                        }
                    ]
                }
            ],
            "errorCode": "Success"
        }
    ],
    "namespace": "Microsoft.Network/applicationGateways",
    "resourceregion": "japaneast"
}

'''