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

    #这里要设置订阅名称
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"

   # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    rgname = "sig-rg"

    #MySQl Flexible Server服务器名称
    mysqlflexible_servername = "leizhangproduction-01"
    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    # Create MySQL Client
    mysqlflexiblesvr_client = MySQLManagementClient(
        credential=clientcredential,
        subscription_id=subscription_id
    )

    response = mysqlflexiblesvr_client.servers.get(rgname,mysqlflexible_servername)
    print(response)

if __name__ == "__main__":
    main()