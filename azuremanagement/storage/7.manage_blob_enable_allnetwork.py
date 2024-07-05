
import os

from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient


def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    resourcegroup_name = "test-rg"
    storageaccount_name = "leiteststorage000"

    virtualnetwork_name = "test-hub-vnet-2"
    subnet_name_1 = "subnet-1"
    subnet_name_2 = "subnet-2"
    subnet_name_3 = "subnet-3"

    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    # # For other authentication approaches, please see: https://pypi.org/project/azure-identity/
    storage_client = StorageManagementClient(
        credential = clientcredential,
        subscription_id = subscription_id
    )

    network_client = NetworkManagementClient(
        credential = clientcredential,
        subscription_id = subscription_id
    )
    subnetname1 = network_client.subnets.get(resourcegroup_name,virtualnetwork_name,subnet_name_1)
    subnetname2 = network_client.subnets.get(resourcegroup_name,virtualnetwork_name,subnet_name_2)
    subnetname3 = network_client.subnets.get(resourcegroup_name,virtualnetwork_name,subnet_name_3)
    
    #https://learn.microsoft.com/en-us/python/api/azure-mgmt-storage/azure.mgmt.storage.v2021_09_01.models.storageaccountupdateparameters?view=azure-python

    #storage = storage_client.storage_accounts.get_properties(resourcegroup_name,storageaccount_name)
    # 设置服务终结点
    params = {
    #'enable_https_traffic_only': True,
    'public_network_access': 'Enabled',
    'network_rule_set': 
    {
        'default_action': 'Allow'
        }
    }
    # Update storage account
    storage_account = storage_client.storage_accounts.update(
        resourcegroup_name,storageaccount_name,params)

    print("Get storage account:\n{}".format(storage_account))


if __name__ == "__main__":
    main()