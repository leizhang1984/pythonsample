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

    # PE的资源组名称
    pe_rg_name = "sig-rg"
    # 要创建的Redis名称
    pe_redisname = "leiredispremium-test-01"
    # PE的订阅ID
    pe_subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    redisclient = RedisManagementClient(credential = clientcredential, subscription_id = pe_subscription_id)
    
    #设置数据中心区域
    location = "germanywestcentral"

            
    '''
    **Note:** Configuring the number of replicas per master is only available when using the Premium SKU and cannot be used in conjunction with shards.
    If both `replicas_per_primary` and `replicas_per_master` are set, they need to be equal.
    
    ''' 
    #创建Redis Standard
    redis = redisclient.redis.begin_create(
        pe_rg_name,
        pe_redisname,
        {
          "location": location,
          #只有Premium，才可以指定Availability Zone
          "zones": [
            "1",
            "2",
            "3"
          ],
          #replicas_per_master 必须是2或者3,  zones才支持设设置为1,2,3
          # If both replicas_per_primary and replicas_per_master are set, they need to be equal.
          "replicas_per_primary": 3,
          "replicas_per_master": 3,
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
          "disable_access_key_authentication": False,
          "minimum_tls_version": "1.2",
          "tags": {
            "SKU": "Premium",
            "Service Id": "0001",
            "Cost Center": "0002"
          }
        }
    ).result()

if __name__ == '__main__':
    main()