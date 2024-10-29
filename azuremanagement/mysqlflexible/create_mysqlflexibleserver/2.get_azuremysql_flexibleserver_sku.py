import os

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.privatedns import PrivateDnsManagementClient
from azure.mgmt.rdbms.mysql_flexibleservers import MySQLManagementClient

'''
https://learn.microsoft.com/en-us/rest/api/mysql/flexibleserver/location-based-capabilities/list?view=rest-mysql-flexibleserver-2023-12-30&tabs=HTTP
'''

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    #这里要设置订阅名称
    pe_dnszone_subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"

   # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    network_client = NetworkManagementClient(
        credential=clientcredential,
        subscription_id=pe_dnszone_subscription_id
    )

    privatedns_management_client = PrivateDnsManagementClient(
        credential=clientcredential,
        subscription_id=pe_dnszone_subscription_id
    )
    #PE订阅下，VPC所在的资源组名称
    rgname = "sig-rg"

    #找到之前创建的虚拟网络名称
    virtualnetwork_name = "NIO-PE-EU"
    #子网名称
    subnet_name = "STG-EU-AZURE-PE-BE-MYSQL-01"
    subnet = network_client.subnets.get(rgname,virtualnetwork_name,subnet_name)
    subnet_id = subnet.id

    #找到之前创建的Private DNS Zone
    privatednzone_name = "leizhangproduction-01.private.mysql.database.azure.com"
    privatre_dnszone = privatedns_management_client.private_zones.get(rgname, privatednzone_name)
    #获得这个Private DNS Zone ID
    private_dnszone_id = privatre_dnszone.id



    #MySQl Flexible Server服务器名称，需要和上面的Private DNS Zone名称一致
    mysqlflexible_servername = "leizhangproduction-01"
    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    # Create MySQL Client
    mysqlflexiblesvr_client = MySQLManagementClient(
        credential=clientcredential,
        subscription_id=pe_dnszone_subscription_id
    )

    #数据中心区域
    location = "germanywestcentral"

    results = mysqlflexiblesvr_client.location_based_capabilities.list(location)
    for result in results:
        print(result)

if __name__ == "__main__":
    main()