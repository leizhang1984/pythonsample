import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.redis import RedisManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.privatedns import PrivateDnsManagementClient
from azure.mgmt.resource import ResourceManagementClient

'''
https://learn.microsoft.com/en-us/python/api/azure-mgmt-redis/azure.mgmt.redis.models.rediscreateparameters?view=azure-python

1.先创建网卡资源


'''

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')
    
    #PE的订阅ID
    pe_subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'
    #PE的资源组名称
    pe_rg_name = "sig-rg"

    #DD的订阅ID
    dd_subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'
    #DD的资源组名称
    dd_rg_name = "sig-rg"
    
    #设置数据中心区域
    location = "germanywestcentral"

    #之前创建好的Redis名称
    pe_redis_name = "leiredispremium01"
    #新建的链接名称
    pe_pvt_endpoint_name = pe_redis_name + "-pvtendpoint"
    #新建链接的时候，会创建1个网卡，设置网卡的名称
    pe_pvt_endpont_nic_name =  pe_pvt_endpoint_name +"-nic"

    #之前创建好的Virtual Network Name
    pe_vnet_name = "NIO-PE-EU"

    #之前创建好的subnet name
    pe_subnet_name = "STG-EU-AZURE-PE-BE-REDIS-01"

    #实例化对象
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    redis_client = RedisManagementClient(credential = clientcredential, subscription_id = pe_subscription_id)
    network_client =  NetworkManagementClient(credential = clientcredential, subscription_id = pe_subscription_id)

    #Private DNS Zone创建在DD订阅里
    privatezone_client = PrivateDnsManagementClient(credential = clientcredential, subscription_id = dd_subscription_id)

    #1.先获得Redis的资源ID
    redis = redis_client.redis.get(pe_rg_name,pe_redis_name)
    redis_id = redis.id

    #2.再获得Redis链接到的Virtual Network的信息，还有子网的信息
    subnet = network_client.subnets.get(pe_rg_name,pe_vnet_name,pe_subnet_name)
    subnet_id = subnet.id

    #这里写死redisCache
    redisCache = "redisCache"
    group_ids = list(redisCache.split(" "))

    #3.创建Private Link Endpoint
    response = network_client.private_endpoints.begin_create_or_update(
        pe_rg_name,
        pe_pvt_endpoint_name,
        {
            "location": location,
            "custom_network_interface_name": pe_pvt_endpont_nic_name,
            "private_link_service_connections": [
            {
              "name": pe_pvt_endpoint_name,
              #需要链接的Redis资源ID
              "private_link_service_id": redis_id,
              #Group Ids这里用redisCache
              "group_ids": group_ids
            }
          ],
          "subnet": {
            "id": subnet_id
          }
        }
    ).result()

    print(response)
    
    #4. 先拿到Private Endpoint里面已经设置好的内网IP地址
    pvt_endpoint = network_client.private_endpoints.get(pe_rg_name,pe_pvt_endpoint_name)
    pvt_endpoint_privateip = pvt_endpoint.custom_dns_configs[0].ip_addresses[0]
    pvt_endpoint_privateip_list = list(pvt_endpoint_privateip.split(" "))

    
    #5.上面设置完毕后，还需要更新private dns zone group
    #指向到之前创建的Private DNS Zone
    #https://learn.microsoft.com/en-us/rest/api/virtualnetwork/private-dns-zone-groups/create-or-update?view=rest-virtualnetwork-2024-01-01&tabs=HTTP

    #先找到private dns zone所在的资源组名称
    #有可能和redis不在一个资源组里

    #不要修改下面的值
    dd_privatednszone_name = "privatelink.redis.cache.windows.net"

    #设置group name
    privatednszone_group_name = "privatelink-redis-cache-windows-net"
    privatednszone_group_fqdn_name = pe_redis_name + "." + dd_privatednszone_name

    dd_private_dnszone = privatezone_client.private_zones.get(dd_rg_name,dd_privatednszone_name)
    dd_private_dnszone_id = dd_private_dnszone.id

    # https://learn.microsoft.com/en-us/python/api/azure-mgmt-network/azure.mgmt.network.operations.privatednszonegroupsoperations?view=azure-python

    response = network_client.private_dns_zone_groups.begin_create_or_update(
        dd_rg_name,
        pe_pvt_endpoint_name,
        #设置name 为 default
        private_dns_zone_group_name = "default",
        parameters={
        #    "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/defaultrg/providers/Microsoft.Network/privateEndpoints/leiredisstd01-pvtendpoint2/privateDnsZoneGroups/default",
           # "name": "default",
            "properties": {
                "privateDnsZoneConfigs": [
                    {
                        "name": privatednszone_group_name,
                        "properties":{
                            "privateDnsZoneId": dd_private_dnszone_id,
                            "record_sets":[
                                {
                                    "record_type": "A",
                                    "record_set_name":pe_redis_name,
                                    "fqdn": privatednszone_group_fqdn_name,
                                    "ttl": 10,
                                    "ip_addresses": pvt_endpoint_privateip_list
                                }
                            ]
                        }
                    }
                ]
            }
        },
    ).result()
    print(response)


if __name__ == '__main__':
    main()