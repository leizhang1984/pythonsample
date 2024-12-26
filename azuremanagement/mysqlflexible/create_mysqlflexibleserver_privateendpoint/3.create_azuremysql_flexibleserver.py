import os

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.privatedns import PrivateDnsManagementClient
from azure.mgmt.rdbms.mysql_flexibleservers import MySQLManagementClient
'''
https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/rdbms/azure-mgmt-rdbms/generated_samples/mysql/server_create.py

需要提前创建好资源：
1.虚拟网络
2.子网
3.Private DNS Zone
'''

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    #这里要设置PE订阅ID
    pe_subscription_id = "c4959ac6-4963-4b67-90dd-da46865b607f"

    #DD的订阅ID
    dd_subscription_id = "074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb"

    #Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    pe_network_client = NetworkManagementClient(
        credential=clientcredential,
        subscription_id = pe_subscription_id
    )

    dd_privatedns_management_client = PrivateDnsManagementClient(
        credential=clientcredential,
        subscription_id=dd_subscription_id
    )
    #资源组名称
    rgname = "defaultrg"

    #找到之前创建的虚拟网络名称
    virtualnetwork_name = "NIO-PE-EU"
    #子网名称
    subnet_name = "STG-EU-AZURE-PE-BE-MYSQL-01"
    subnet = pe_network_client.subnets.get(rgname,virtualnetwork_name,subnet_name)
    subnet_id = subnet.id

    #找到之前创建的Private DNS Zone
    privatednzone_name = "privatelink.mysql.database.azure.com"
    privatre_dnszone = dd_privatedns_management_client.private_zones.get(rgname, privatednzone_name)
    #获得这个Private DNS Zone ID
    private_dnszone_id = privatre_dnszone.id

    #MySQl Flexible Server服务器名称，随意输入
    mysqlflexible_servername = "leizhangproduction-00"

    #自定义标签
    custom_tags = {
        'Environment': 'Development',
        'Department': 'IT'
    }

    # Create MySQL Client
    mysqlflexiblesvr_client = MySQLManagementClient(
        credential=clientcredential,
        subscription_id=pe_subscription_id
    )

    #检查MySQL Flexible Server是否存在
    #response = mysqlflexiblesvr_client.servers.get(rgname,mysqlflexible_servername)

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
                    "public_network_access": "Disabled",   #"Disabled"
                    #加入到subnet子网id
                    # "delegated_subnet_resource_id":subnet_id,
                    #关联的private dns zone id
                    "private_dns_zone_resource_id": private_dnszone_id
                },
                "maintenancewindow": {
                    "customwindow":"Enabled",
                    #默认是UTC时区，北京时间是UTC+8
                    "dayofweek": 0,   # 0表示星期天，1表示星期一，依此类推
                    "starthour": 2,   # 维护窗口的开始小时（0-23）
                    "startminute": 0  # 维护窗口的开始分钟（0-59）
                }
            },
            "sku": {"name": "Standard_D2ds_v4", "tier": "GeneralPurpose"},
            "tags": custom_tags,
        },
    ).result()
    print(response)




if __name__ == "__main__":
    main()