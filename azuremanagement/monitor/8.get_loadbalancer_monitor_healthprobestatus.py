import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.network import NetworkManagementClient


def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'
    rg_name = "sig-rg"
    loadbalacer_name = "NIO-EU-Hadoop-VMSS-2LB"
    
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    network_client = NetworkManagementClient(credential=clientcredential, subscription_id = subscription_id)
    monitor_client = MonitorManagementClient(credential=clientcredential, subscription_id = subscription_id)

    #获得负载均衡器信息
    load_balancer = network_client.load_balancers.get(rg_name,loadbalacer_name)
    resource_id = load_balancer.id

    timespan = '2024-05-21T01:40:00Z/2024-05-21T07:41:00Z'
    metricnamespace = 'Microsoft.Network/loadBalancers'

    #Support Metric
    #https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-network-loadbalancers-metrics
    #Health Probe Status = DipAvailability

    #拿到负载均衡器后端的ip地址，具体步骤略。
    #我这里后端的ip分别是：10.99.76.10 和10.99.76.14

    #internal PT1H 代表每1小时
    #DipAvailability代表Health Probe Status
    #
    result1 = monitor_client.metrics.list(resource_id,timespan,"PT1H","DipAvailability","average,minimum,maximum",None,None,"BackendIPAddress eq '10.99.76.10'")
  
    print(result1)



if __name__ == '__main__':
    main()

###############################   samle result
###############################
###############################
###############################
# {
#     "cost": 897,
#     "timespan": "2024-05-22T01:27:00Z/2024-05-22T06:27:00Z",
#     "interval": "PT1H",
#     "value": [
#         {
#             "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/sig-rg/providers/Microsoft.Network/loadBalancers/NIO-EU-Hadoop-VMSS-2LB/providers/Microsoft.Insights/metrics/DipAvailability",
#             "type": "Microsoft.Insights/metrics",
#             "name": {
#                 "value": "DipAvailability",
#                 "localizedValue": "Health Probe Status"
#             },
#             "displayDescription": "Average Load Balancer health probe status per time duration",
#             "unit": "Count",
#             "timeseries": [
#                 {
#                     "metadatavalues": [],
#                     "data": [
#                         {
#                             "timeStamp": "2024-05-22T01:27:00Z"
#                         },
#                         {
#                             "timeStamp": "2024-05-22T02:27:00Z"
#                         },
#                         {
#                             "timeStamp": "2024-05-22T03:27:00Z"
#                         },
#                         {
#                             "timeStamp": "2024-05-22T04:27:00Z"
#                         },
#                         {
#                             "timeStamp": "2024-05-22T05:27:00Z",
#                             "average": 89.65517241379311,
#                             "minimum": 0,
#                             "maximum": 100
#                         }
#                     ]
#                 }
#             ],
#             "errorCode": "Success"
#         }
#     ],
#     "namespace": "Microsoft.Network/loadBalancers",
#     "resourceregion": "germanywestcentral"
# }
