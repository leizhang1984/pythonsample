import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.redis import RedisManagementClient
from azure.mgmt.network import NetworkManagementClient

'''
https://learn.microsoft.com/en-us/python/api/azure-mgmt-redis/azure.mgmt.redis.models.rediscreateparameters?view=azure-python

1.先创建Redis Cache, 设置SKU为Premium
2.创建完毕后, 再private Endpoint link到redis子网上

'''

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    rg_name = "defaultrg"
    redisname = "leiredispremium01"
    subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    redisclient = RedisManagementClient(credential = clientcredential, subscription_id = subscription_id)
    
    #设置数据中心区域
    location = "germanywestcentral"

    #创建Redis Standard
    redis = redisclient.redis.begin_create(
        rg_name,
        redisname,
        {
          "location": location,
          #Premium可以指定Availability Zone
          "zones": [
            "1",
            "2"
          ],
          #SKU为Premium P1, 6GB
          #具体的SKU可以参考：https://azure.microsoft.com/zh-cn/pricing/details/cache/
          "sku": {
            "name": "Premium",
            "family": "P",
            "capacity": "1"
          },
          "redis_version": "latest",
          "enable_non_ssl_port": True,
          "public_network_access": "Enabled",
          "disable_access_key_authentication": "Disabled",
          "minimum_tls_version": "1.2"
        }
    ).result()

if __name__ == '__main__':
    main()