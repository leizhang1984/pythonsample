import os

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.privatedns import PrivateDnsManagementClient
from azure.mgmt.network import NetworkManagementClient

'''
这里的代码只需要在创建private dns zone的时候，执行1次就可以了
'''

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')


    #这里要设置订阅名称,是MySQL RDS新建的Private DNS Zone
    pe_dnszone_subscription_id = "c4959ac6-4963-4b67-90dd-da46865b607f"

    #这里要设置订阅名称，是DD订阅下的，已经有的Private DNS Zone
    dd_dnszone_subscription_id = "074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb"
    
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
    dd_rgname = "defaultrg"
    #DD订阅，要创建的Private DNSZone名称
    dd_privatednzone_name = "privatelink.mysql.database.azure.com"  

    #PE订阅，资源组名称
    pe_rgname = "defaultrg"
    #PE要建立Virtual Network的VPC名称
    pe_virtualnetwork_name_1 = "NIO-PE-EU"
    pe_virtualnetwork_name_2 = "NIO-PE-EU-OPS"

    #自定义标签
   # 自定义标签
    custom_tags = {
                    "Environment": "stg",
                    "Department": "POW",
                    "ServiceInstance": "pe-db-stg"
    }
    ###########################
    #1.首先在DD订阅下，新建Private DNS Zone
    response = dd_privatedns_management_client.private_zones.begin_create_or_update(
        dd_rgname, dd_privatednzone_name, parameters={"location": "Global", "tags": custom_tags},
    ).result()

    print(response)

    ###########################
    #2.新建Private DNS Zone后，还要与DD已有的OPS VPC建立Link关系
    #DD订阅的资源组名称
    #DD订阅，要建立Virtual Network的VPC名称
    dd_virtualnetwork_name = "NIO-EU-OPS"

    dd_network_client = NetworkManagementClient(
        credential = clientcredential,
        subscription_id = dd_dnszone_subscription_id
    )

    dd_virtualnetwork = dd_network_client.virtual_networks.get(dd_rgname,dd_virtualnetwork_name)

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
            "tags": custom_tags,
        },
    ).result()

    ###########
    #3.新建Private DNS Zone后，还要与PE EU link

    pe_network_client = NetworkManagementClient(
        credential = clientcredential,
        subscription_id = pe_dnszone_subscription_id
    )

    pe_virtualnetwork = pe_network_client.virtual_networks.get(pe_rgname,pe_virtualnetwork_name_1)

    dd_privatedns_management_client.virtual_network_links.begin_create_or_update(
        resource_group_name = pe_rgname,
        private_zone_name = dd_privatednzone_name,
        virtual_network_link_name = "link-pe-eu",
        parameters={
            "location": "Global",
            "properties": {
                "registrationEnabled": False,
                "virtualNetwork": {
                    "id": pe_virtualnetwork.id
                },
            },
            "tags": custom_tags,
        },
    ).result()



    ###########
    #3.新建Private DNS Zone后，还要与PE EU OPS link


    pe_network_client = NetworkManagementClient(
        credential = clientcredential,
        subscription_id = pe_dnszone_subscription_id
    )

    pe_virtualnetwork = pe_network_client.virtual_networks.get(pe_rgname,pe_virtualnetwork_name_2)

    dd_privatedns_management_client.virtual_network_links.begin_create_or_update(
        resource_group_name = pe_rgname,
        private_zone_name = dd_privatednzone_name,
        virtual_network_link_name = "link-pe-eu-ops",
        parameters={
            "location": "Global",
            "properties": {
                "registrationEnabled": False,
                "virtualNetwork": {
                    "id": pe_virtualnetwork.id
                },
            },
            "tags": custom_tags,
        },
    ).result()

if __name__ == "__main__":
    main()