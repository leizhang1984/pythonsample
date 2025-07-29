import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.network import NetworkManagementClient

'''

监控Azure专线网关的指标：Max Flows Create Per Seconds
具体的MetricNamespace等信息，可以参考
https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-network-virtualnetworkgateways-metrics

'''
def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_tenantid')
    clientsecret = os.environ.get('nonprod_clientsecret')
    
    #订阅ID
    sub_id = '074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb'

    #credentials = DefaultAzureCredential()
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    monitor_client = MonitorManagementClient(credential = clientcredential, subscription_id = sub_id)
    network_client = NetworkManagementClient(credential = clientcredential, subscription_id = sub_id)
    
    #monitor_client = MonitorManagementClient(credentials, subscription_id = sub_id)
    #network_client = NetworkManagementClient(credentials, subscription_id = sub_id)

    #virtual_network_gw_name
    rg_name = 'defaultrg'
    virtual_network_gw_name = 'NIO-EU-ERGW-TOFRDC'

    virtual_network_gw = network_client.virtual_network_gateways.get(rg_name,virtual_network_gw_name)
    virtual_network_gw_id = virtual_network_gw.id
    
    # P1Y：表示 1 年。
    # P2M：表示 2 个月。
    # P3W：表示 3 周。
    # P4D：表示 4 天。
    # PT5H：表示 5 小时。
    # PT6M：表示 6 分钟。
    # PT7S：表示 7 秒。

    #P7D表示最近15天
    timespan = 'P15D'
    metricnamespace = 'microsoft.network/virtualnetworkgateways'
    metric = 'ExpressRouteGatewayMaxFlowsCreationRate'

    #间隔5分钟
    #interval = 'PT5M'
    interval = 'P1D'

    metric_result = monitor_client.metrics.list(
        virtual_network_gw_id,
        timespan,interval,
        metric,"maximum",None,None,None)
    
    for result in metric_result.value[0].timeseries[0].data:
        print("监控的时间是:", result.time_stamp)
        print("监控的最大值是:", result.maximum)



if __name__ == '__main__':
    main()