import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.redis import RedisManagementClient
from azure.mgmt.network import NetworkManagementClient

'''
https://learn.microsoft.com/en-us/python/api/azure-mgmt-redis/azure.mgmt.redis.models.rediscreateparameters?view=azure-python

1.更新Redis维护窗口
2.只能在创建完Redis Cache后才可以更新

'''

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    # PE的资源组名称
    pe_rg_name = "sig-rg"
    # 要创建的Redis名称
    pe_redisname = "leiredisstd01"
    # PE的订阅ID
    pe_subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'

    #设置数据中心区域
    location = "germanywestcentral"

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    redisclient = RedisManagementClient(credential = clientcredential, subscription_id = pe_subscription_id)
    
    #更新Redis维护窗口
    response = redisclient.patch_schedules.create_or_update(
        pe_rg_name,
        pe_redisname,
        default="default",
        parameters={
            "properties": {
                "scheduleEntries": [
                    #维护窗口开始时间是UTC时区，请注意北京时间是UTC+8时区
                    #更新创建至少需要5小时
                    {"dayOfWeek": "Monday", "maintenanceWindow": "PT5H", "startHourUtc": 12},
                    {"dayOfWeek": "Tuesday","maintenanceWindow": "PT5H", "startHourUtc": 12},
                    {"dayOfWeek": "Wednesday","maintenanceWindow": "PT5H", "startHourUtc": 12}
                ]
            }
        },
    )
    print(response)

if __name__ == '__main__':
    main()