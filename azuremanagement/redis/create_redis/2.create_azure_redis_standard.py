import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.redis import RedisManagementClient
from azure.mgmt.network import NetworkManagementClient

'''
https://learn.microsoft.com/en-us/python/api/azure-mgmt-redis/azure.mgmt.redis.models.rediscreateparameters?view=azure-python

1.先创建Redis Cache, 设置SKU为Standard
2.创建完毕后, 再private Endpoint link到redis子网上

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
    

    #创建Redis Standard
    redis = redisclient.redis.begin_create(
        pe_rg_name,
        pe_redisname,
        {
          "location": location,
          #SKU为Standard C1, 1GB
          #具体的SKU可以参考：https://azure.microsoft.com/zh-cn/pricing/details/cache/
          "sku": {
            "name": "Standard",
            "family": "C",
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