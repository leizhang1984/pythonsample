import os

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.privatedns import PrivateDnsManagementClient
from azure.mgmt.rdbms.mysql_flexibleservers import MySQLManagementClient

'''
https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/rdbms/azure-mgmt-rdbms/generated_samples/mysql_flexibleservers/server_create.py

需要提前创建好资源：
1.虚拟网络
2.子网
3.Private DNS Zone
'''

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    #这里要设置PE订阅名称
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"

   # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    network_client = NetworkManagementClient(
        credential=clientcredential,
        subscription_id=subscription_id
    )

    privatedns_management_client = PrivateDnsManagementClient(
        credential=clientcredential,
        subscription_id=subscription_id
    )
    #资源组名称
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

    # Create MySQL Client
    mysqlflexiblesvr_client = MySQLManagementClient(
        credential=clientcredential,
        subscription_id=subscription_id
    )

    response = mysqlflexiblesvr_client.servers.begin_create(
        rgname,
        mysqlflexible_servername,
        parameters={
            "location": "germanywestcentral",
            "properties": {
                "administratorLogin": "mysqladmin",
                "administratorLoginPassword": "Thisis@mypassword123456",
                #主服务器，在可用区1
                #如果设置 "availabilityZone": "",为空，则在任意一个可用区部署
                "availabilityZone": "",
                "backup": {"backupRetentionDays": 7, "geoRedundantBackup": "Disabled"},
                "createMode": "Default",
                #高可用服务器，在可用区3
                #如果设置 "availabilityZone": "",为空，则在任意一个可用区部署
                "highAvailability": {"mode": "ZoneRedundant", "standbyAvailabilityZone": ""},
                "storage": {
                    "autoGrow": "Enabled",
                    "iops": "600",
                    "storageRedundancy": "LocalRedundancy",
                    "storageSizeGB": 100,
                },
                "version": "8.0.21",
                "network":{
                    #不允许公网访问
                    "public_network_access": "Disabled",
                    #加入到subnet子网id
                    "delegated_subnet_resource_id":subnet_id,
                    #关联的private dns zone id
                    "private_dns_zone_resource_id": private_dnszone_id
                }
            },
            "sku": {"name": "Standard_D2ds_v4", "tier": "GeneralPurpose"},
            "tags": {"num": "1"},
        },
    ).result()
    print(response)




if __name__ == "__main__":
    main()