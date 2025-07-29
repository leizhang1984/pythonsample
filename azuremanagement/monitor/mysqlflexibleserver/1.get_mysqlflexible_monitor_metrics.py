import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.rdbms.mysql_flexibleservers import MySQLManagementClient
#pip3 install azure-mgmt-rdbms


def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'
    rg_name = "sig-rg"
    mysqlserver_name = "leimysqlflexiblesvr01"
    
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    mysqlmanagement_client = MySQLManagementClient(credential=clientcredential, subscription_id = subscription_id)
    monitor_client = MonitorManagementClient(credential=clientcredential, subscription_id = subscription_id)

    #获得MySQL Flexible Server信息
    mysqlserver = mysqlmanagement_client.servers.get(rg_name,mysqlserver_name)
    resource_id = mysqlserver.id

    #统计的开始时间/统计的结束时间，我这里用UTC时区
    timespan = '2024-07-11T09:30:00Z/2024-07-11T09:41:00Z'
    #metricnamespace这个不用改
    metricnamespace = 'Microsoft.DBforMySQL/flexibleServers'

    #Support Metric
    #https://learn.microsoft.com/zh-cn/azure/azure-monitor/reference/supported-metrics/microsoft-dbformysql-flexibleservers-metrics

    #memory_percent代表： 内存百分比

    #internal PT1H 代表每1小时
    #internal PT1M 代表每1分钟
    metric_result = monitor_client.metrics.list(resource_id,timespan,"PT1M","memory_percent","average,minimum,maximum",None,None,None)
    print(metric_result)

    #CALL REST API
    #https://management.azure.com/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/sig-rg/providers/Microsoft.DBforMySQL/flexibleservers/leimysqlflexiblesvr01/providers/Microsoft.Insights/metrics?api-version=2023-10-01&aggregation=average,minimum,maximum&interval=PT1M&metricnames=memory_percent&metricnamespace=Microsoft.DBforMySQL/flexibleServers&timespan=2024-07-11T09:30:00Z/2024-07-11T09:41:00Z&AutoAdjustTimegrain=True&ValidateDimensions=False

if __name__ == '__main__':
    main()


    '''
   {
    "cost": 30,
    "timespan": "2024-07-11T09:30:00Z/2024-07-11T09:41:00Z",
    "interval": "PT1M",
    "value": [
        {
            "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/sig-rg/providers/Microsoft.DBforMySQL/flexibleservers/leimysqlflexiblesvr01/providers/Microsoft.Insights/metrics/memory_percent",
            "type": "Microsoft.Insights/metrics",
            "name": {
                "value": "memory_percent",
                "localizedValue": "Memory Percent"
            },
            "displayDescription": "Memory Percent",
            "unit": "Percent",
            "timeseries": [
                {
                    "metadatavalues": [],
                    "data": [
                        {
                            "timeStamp": "2024-07-11T09:30:00Z",
                            "average": 23.09,
                            "minimum": 23.09,
                            "maximum": 23.09
                        },
                        {
                            "timeStamp": "2024-07-11T09:31:00Z",
                            "average": 23.055,
                            "minimum": 23.01,
                            "maximum": 23.1
                        },
                        {
                            "timeStamp": "2024-07-11T09:32:00Z",
                            "average": 23.01,
                            "minimum": 23.01,
                            "maximum": 23.01
                        },
                        {
                            "timeStamp": "2024-07-11T09:33:00Z",
                            "average": 23.01,
                            "minimum": 23.01,
                            "maximum": 23.01
                        },
                        {
                            "timeStamp": "2024-07-11T09:34:00Z",
                            "average": 23.01,
                            "minimum": 23.01,
                            "maximum": 23.01
                        },
                        {
                            "timeStamp": "2024-07-11T09:35:00Z",
                            "average": 23.01,
                            "minimum": 23.01,
                            "maximum": 23.01
                        },
                        {
                            "timeStamp": "2024-07-11T09:36:00Z",
                            "average": 23.01,
                            "minimum": 23.01,
                            "maximum": 23.01
                        },
                        {
                            "timeStamp": "2024-07-11T09:37:00Z",
                            "average": 23.115,
                            "minimum": 23.01,
                            "maximum": 23.22
                        },
                        {
                            "timeStamp": "2024-07-11T09:38:00Z",
                            "average": 23.22,
                            "minimum": 23.22,
                            "maximum": 23.22
                        },
                        {
                            "timeStamp": "2024-07-11T09:39:00Z",
                            "average": 23.22,
                            "minimum": 23.22,
                            "maximum": 23.22
                        },
                        {
                            "timeStamp": "2024-07-11T09:40:00Z",
                            "average": 22.855,
                            "minimum": 22.78,
                            "maximum": 22.93
                        }
                    ]
                }
            ],
            "errorCode": "Success"
        }
    ],
    "namespace": "Microsoft.DBforMySQL/flexibleServers",
    "resourceregion": "germanywestcentral"
}
    '''