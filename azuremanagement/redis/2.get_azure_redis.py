import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.redis import RedisManagementClient
from azure.mgmt.network import NetworkManagementClient

tenantid = os.environ.get('tenantid')
clientid = os.environ.get('clientid')
clientsecret = os.environ.get('clientsecret')

def main():
    rg_name = "default-rg"
    redisname = "s-azure-test"
    subscription_id = '074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb'

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    redisclient = RedisManagementClient(credential = clientcredential, subscription_id = subscription_id)

    redis = redisclient.redis.get(rg_name,redisname)

    print(redis.name)
    print(redis.subnet_id)

    result = redis.subnet_id.split("/")

    #虚拟网络名称
    vnetname = result[8]
    print(vnetname)

    #子网名称
    subnetname = result[10]
    print(subnetname)

    networkclient = NetworkManagementClient(credential = clientcredential, subscription_id = subscription_id)

    #按照虚拟网络名称和子网名称 ，获得改子网信息
    subnetinfo = networkclient.subnets.get(rg_name,vnetname,subnetname)
    print(subnetinfo.address_prefix)

if __name__ == '__main__':
    main()