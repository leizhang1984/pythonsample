import os

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.privatedns import PrivateDnsManagementClient

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
    #要创建的Private DNSZone名称
    privatednzone_name = "leizhangproduction-01.private.mysql.database.azure.com"

    #因为不建议在PE订阅下创建Private DNS Zone
    #所以，列出该订阅下，所有的Private DNS
    response = privatedns_management_client.private_zones.begin_create_or_update(
        rgname, privatednzone_name, parameters={"location": "Global", "tags": {"key1": "value1"}},
    ).result()

    print(response)



if __name__ == "__main__":
    main()