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

    #这里要设置PE订阅名称
    pe_dnszone_subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"

   # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    # Create MySQL Client
    mysqlflexiblesvr_client = MySQLManagementClient(
        credential = clientcredential,
        subscription_id = pe_dnszone_subscription_id
    )

    #数据中心区域
    location = "germanywestcentral"

    results = mysqlflexiblesvr_client.location_based_capabilities.list(location)
    for result in results:
        print(result)

if __name__ == "__main__":
    main()