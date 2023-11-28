from azure.identity import DefaultAzureCredential
from azure.mgmt.redis import RedisManagementClient
from azure.mgmt.network import NetworkManagementClient

rg_name = "default-rg"
redisname = "s-azure-test"

redisclient = RedisManagementClient(credential=DefaultAzureCredential(), subscription_id = "074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb")

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

networkclient = NetworkManagementClient(credential=DefaultAzureCredential(), subscription_id = "074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb")

#按照虚拟网络名称和子网名称 ，获得改子网信息
subnetinfo = networkclient.subnets.get(rg_name,vnetname,subnetname)
print(subnetinfo.address_prefix)
