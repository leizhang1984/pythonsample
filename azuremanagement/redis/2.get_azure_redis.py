import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.redis import RedisManagementClient
from azure.mgmt.network import NetworkManagementClient

tenantid = os.environ.get('nonprod_tenantid')
clientid = os.environ.get('nonprod_clientid')
clientsecret = os.environ.get('nonprod_clientsecret')

def main():
    rg_name = "sig-rg"
    redisname = "leiredistest01"
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    redisclient = RedisManagementClient(credential = clientcredential, subscription_id = subscription_id)

    redis = redisclient.redis.get(rg_name,redisname)

    print(redis.name)
    print(redis.subnet_id)
    #获得isMaster信息

    instances = redis.instances
    for instance in instances:
        print(instance.ssl_port)
        print(instance.is_master)
        print(instance.is_primary)

    # result = redis.subnet_id.split("/")

    # #虚拟网络名称
    # vnetname = result[8]
    # print(vnetname)

    # #子网名称
    # subnetname = result[10]
    # print(subnetname)

    # networkclient = NetworkManagementClient(credential = clientcredential, subscription_id = subscription_id)

    # #按照虚拟网络名称和子网名称 ，获得改子网信息
    # subnetinfo = networkclient.subnets.get(rg_name,vnetname,subnetname)
    # print(subnetinfo.address_prefix)

if __name__ == '__main__':
    main()