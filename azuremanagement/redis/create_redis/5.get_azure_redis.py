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
    pe_redisname = "leiredispremium01"
    # PE的订阅ID
    pe_subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    redisclient = RedisManagementClient(credential = clientcredential, subscription_id = pe_subscription_id)
    
    #设置数据中心区域
    location = "germanywestcentral"

    #创建Redis Standard
    result = redisclient.redis.get(pe_rg_name,pe_redisname)
    print(result)

if __name__ == '__main__':
    main()