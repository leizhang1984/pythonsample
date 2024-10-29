import os

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.privatedns import PrivateDnsManagementClient

"""
# PREREQUISITES
    pip install azure-identity
    pip install azure-mgmt-privatedns
# USAGE
    python private_zone_get.py

    Before run the sample, please set the values of the client ID, tenant ID and client secret
    of the AAD application as environment variables: AZURE_CLIENT_ID, AZURE_TENANT_ID,
    AZURE_CLIENT_SECRET. For more info about how to get the value, please see:
    https://docs.microsoft.com/azure/active-directory/develop/howto-create-service-principal-portal
"""

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    #这里要设置订阅名称，比如PE
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"

    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    privatedns_management_client = PrivateDnsManagementClient(
        credential=clientcredential,
        subscription_id=subscription_id
    )

    #因为不建议在PE订阅下创建Private DNS Zone
    #所以，列出该订阅下，所有的Private DNS
    private_zones = privatedns_management_client.private_zones.list()
    for privatezone in private_zones:
        print(privatezone)


if __name__ == "__main__":
    main()