import os

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.privatedns import PrivateDnsManagementClient
from azure.mgmt.rdbms.mysql_flexibleservers import MySQLManagementClient

'''
https://github.com/Azure/azure-sdk-for-python/blob/main/sdk/rdbms/azure-mgmt-rdbms/generated_samples/mysql_flexibleservers/configurations_batch_update.py
'''

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    #这里要设置订阅名称
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"

   # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    privatedns_management_client = PrivateDnsManagementClient(
        credential=clientcredential,
        subscription_id=subscription_id
    )
    #资源组名称
    rgname = "defaultrg"
    #MySQL Flexible Server Name
    mysqlflexible_servername = "leizhangproduction-01"

    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    # Create MySQL Client
    mysqlflexiblesvr_client = MySQLManagementClient(
        credential=clientcredential,
        subscription_id=subscription_id
    )

    response = mysqlflexiblesvr_client.configurations.begin_batch_update(
        rgname,
        mysqlflexible_servername,
        parameters={
            "resetAllToDefault": "False",
            "value": [
                {"name": "event_scheduler", "properties": {"value": "OFF"}},
                {"name": "require_secure_transport", "properties": {"value": "OFF"}},
                {"name": "connect_timeout", "properties": {"value": "30"}},
                {"name": "sql_mode", "properties": {"value": "ERROR_FOR_DIVISION_BY_ZERO,NO_AUTO_CREATE_USER,NO_ZERO_DATE,NO_ZERO_IN_DATE,ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES"}},
            ],
        },
    ).result()
    print(response)

    #按照需要，对MySQL数据库进行重启
    #response = mysqlflexiblesvr_client.servers.begin_restart(rgname,mysqlflexible_servername).result()
    #print(response)

if __name__ == "__main__":
    main()