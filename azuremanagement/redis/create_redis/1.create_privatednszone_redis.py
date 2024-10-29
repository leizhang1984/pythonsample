import os

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.privatedns import PrivateDnsManagementClient
from azure.mgmt.network import NetworkManagementClient

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    #这里要设置订阅名称,是MySQL RDS新建的Private DNS Zone
    pe_dnszone_subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"

    #这里要设置订阅名称，是DD订阅下的，已经有的Private DNS Zone
    dd_dnszone_subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"

    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    pe_privatedns_management_client = PrivateDnsManagementClient(
        credential = clientcredential,
        subscription_id = pe_dnszone_subscription_id
    )
    
    dd_privatedns_management_client = PrivateDnsManagementClient(
        credential = clientcredential,
        subscription_id = dd_dnszone_subscription_id
    )

    
    #DD订阅，资源组名称
    dd_rgname = "sig-rg"
    #DD订阅，要创建的Private DNSZone名称
    dd_privatednzone_name = "privatelink.redis.cache.windows.net"


    #PE订阅，资源组名称
    pe_rgname = "sig-rg"
    #PE要建立Virtual Network的VPC名称
    pe_virtualnetwork_name = "NIO-PE-EU"

    redis_dns_exist = False
    #1.先找Private DNS Zone是否存在
    results = dd_privatedns_management_client.private_zones.list_by_resource_group(dd_rgname)
    for result in results:
        if result.name == dd_privatednzone_name :
            redis_dns_exist = True
            break


    #2.如果不存在，则新建Private DNS Zone
    if redis_dns_exist == False:
        response = dd_privatedns_management_client.private_zones.begin_create_or_update(
            dd_rgname, dd_privatednzone_name, parameters={"location": "Global", "tags": {"key1": "value1"}},
        ).result()
        print(response)

    #3.DD订阅，要建立Virtual Network的VPC名称
    #DD订阅的资源组名称
    dd_rgname = "sig-rg"

    dd_virtualnetwork_name = "NIO-EU-OPS"

    dd_network_client = NetworkManagementClient(
        credential = clientcredential,
        subscription_id = dd_dnszone_subscription_id
    )

    dd_virtualnetwork = dd_network_client.virtual_networks.get(dd_rgname,dd_virtualnetwork_name)


    #3.检查Private DNS Zone 和DD-OPS VPC是否有Link
    redis_dnslink_exist = False

    results = dd_privatedns_management_client.virtual_network_links.list(dd_rgname,dd_privatednzone_name)
    for result in results:
        if result.virtual_network.id == dd_virtualnetwork.id: 
            redis_dnslink_exist = True
            break


    if redis_dnslink_exist == False:
        dd_privatedns_management_client.virtual_network_links.begin_create_or_update(
            resource_group_name = pe_rgname,
            private_zone_name = dd_privatednzone_name,
            virtual_network_link_name = "link-dd-eu-ops",
            parameters={
                "location": "Global",
                "properties": {
                    "registrationEnabled": False,
                    "virtualNetwork": {
                        "id": dd_virtualnetwork.id
                    },
                },
                "tags": {"key1": "value1"},
            },
        ).result()

        

if __name__ == "__main__":
    main()