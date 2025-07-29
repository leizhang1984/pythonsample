import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.redis import RedisManagementClient


def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'
    rg_name = "sig-rg"
    redis_name = "leiredistest01"
    
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    redis_client = RedisManagementClient(credential=clientcredential, subscription_id = subscription_id)
    monitor_client = MonitorManagementClient(credential=clientcredential, subscription_id = subscription_id)

    #获得Redis信息
    redis = redis_client.redis.get(rg_name,redis_name)
    resource_id = redis.id

    #统计的开始时间/统计的结束时间
    timespan = '2024-07-11T07:00:00Z/2024-07-11T07:41:00Z'
    #metricnamespace这个不用改
    metricnamespace = 'Microsoft.Cache/redis'

    #Support Metric
    #https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cache-redis-metrics
    #usedmemory代表： The amount of cache memory used for key/value pairs in the cache in MB

    #internal PT1H 代表每1小时
    #internal PT1M 代表每1分钟
    metric_result = monitor_client.metrics.list(resource_id,timespan,"PT1M","usedmemory","average,minimum,maximum",None,None,None)
  

    #Call REST API
    #https://management.azure.com/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/sig-rg/providers/Microsoft.Cache/Redis/leiredistest01/providers/Microsoft.Insights/metrics?api-version=2023-10-01&aggregation=average,minimum,maximum&interval=PT1M&metricnames=usedmemory&metricnamespace=Microsoft.Cache/redis&timespan=2024-07-11T07:00:00Z/2024-07-11T07:41:00Z&AutoAdjustTimegrain=True&ValidateDimensions=False
    print(metric_result)


if __name__ == '__main__':
    main()


    '''
    {
    "cost": 120,
    "timespan": "2024-07-11T07:00:00Z/2024-07-11T07:41:00Z",
    "interval": "PT1M",
    "value": [
        {
            "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/sig-rg/providers/Microsoft.Cache/Redis/leiredistest01/providers/Microsoft.Insights/metrics/usedmemory",
            "type": "Microsoft.Insights/metrics",
            "name": {
                "value": "usedmemory",
                "localizedValue": "Used Memory"
            },
            "displayDescription": "The amount of cache memory used for key/value pairs in the cache in MB. For more details, see https://aka.ms/redis/metrics.",
            "unit": "Bytes",
            "timeseries": [
                {
                    "metadatavalues": [],
                    "data": [
                        {
                            "timeStamp": "2024-07-11T07:00:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:01:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:02:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:03:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:04:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:05:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:06:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:07:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:08:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:09:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:10:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:11:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:12:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:13:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:14:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:15:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:16:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:17:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:18:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:19:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:20:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:21:00Z"
                        },
                        {
                            "timeStamp": "2024-07-11T07:22:00Z",
                            "average": 42409592,
                            "minimum": 42358176,
                            "maximum": 42461008
                        },
                        {
                            "timeStamp": "2024-07-11T07:23:00Z",
                            "average": 42389140,
                            "minimum": 42358176,
                            "maximum": 42420104
                        },
                        {
                            "timeStamp": "2024-07-11T07:24:00Z",
                            "average": 42378652,
                            "minimum": 42358176,
                            "maximum": 42399128
                        },
                        {
                            "timeStamp": "2024-07-11T07:25:00Z",
                            "average": 42358176,
                            "minimum": 42358176,
                            "maximum": 42358176
                        },
                        {
                            "timeStamp": "2024-07-11T07:26:00Z",
                            "average": 42358176,
                            "minimum": 42358176,
                            "maximum": 42358176
                        },
                        {
                            "timeStamp": "2024-07-11T07:27:00Z",
                            "average": 42358176,
                            "minimum": 42358176,
                            "maximum": 42358176
                        },
                        {
                            "timeStamp": "2024-07-11T07:28:00Z",
                            "average": 42378652,
                            "minimum": 42358176,
                            "maximum": 42399128
                        },
                        {
                            "timeStamp": "2024-07-11T07:29:00Z",
                            "average": 42358176,
                            "minimum": 42358176,
                            "maximum": 42358176
                        },
                        {
                            "timeStamp": "2024-07-11T07:30:00Z",
                            "average": 42358176,
                            "minimum": 42358176,
                            "maximum": 42358176
                        },
                        {
                            "timeStamp": "2024-07-11T07:31:00Z",
                            "average": 42358176,
                            "minimum": 42358176,
                            "maximum": 42358176
                        },
                        {
                            "timeStamp": "2024-07-11T07:32:00Z",
                            "average": 42358176,
                            "minimum": 42358176,
                            "maximum": 42358176
                        },
                        {
                            "timeStamp": "2024-07-11T07:33:00Z",
                            "average": 42358176,
                            "minimum": 42358176,
                            "maximum": 42358176
                        },
                        {
                            "timeStamp": "2024-07-11T07:34:00Z",
                            "average": 42358176,
                            "minimum": 42358176,
                            "maximum": 42358176
                        },
                        {
                            "timeStamp": "2024-07-11T07:35:00Z",
                            "average": 42358176,
                            "minimum": 42358176,
                            "maximum": 42358176
                        },
                        {
                            "timeStamp": "2024-07-11T07:36:00Z",
                            "average": 42358176,
                            "minimum": 42358176,
                            "maximum": 42358176
                        },
                        {
                            "timeStamp": "2024-07-11T07:37:00Z",
                            "average": 42378652,
                            "minimum": 42358176,
                            "maximum": 42399128
                        },
                        {
                            "timeStamp": "2024-07-11T07:38:00Z",
                            "average": 42358176,
                            "minimum": 42358176,
                            "maximum": 42358176
                        },
                        {
                            "timeStamp": "2024-07-11T07:39:00Z",
                            "average": 42358176,
                            "minimum": 42358176,
                            "maximum": 42358176
                        },
                        {
                            "timeStamp": "2024-07-11T07:40:00Z",
                            "average": 42358176,
                            "minimum": 42358176,
                            "maximum": 42358176
                        }
                    ]
                }
            ],
            "errorCode": "Success"
        }
    ],
    "namespace": "Microsoft.Cache/redis",
    "resourceregion": "germanywestcentral"
}
    '''