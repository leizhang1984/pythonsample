import os

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import *

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')


    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    rg_name = "aks-rg"
    vnet_name = "aks_vnet"
    location = "germanywestcentral"

    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    network_client = NetworkManagementClient(
        credential=clientcredential,
        subscription_id=subscription_id
    )
    #获得vnet
    vnet = network_client.virtual_networks.get(rg_name,vnet_name)
    print("Get VNet:\n{}".format(vnet))


    usages =network_client.virtual_networks.list_usage(rg_name,vnet_name)
    for usage in usages:
        print("Get Usage:\n{}".format(usage))


        

    
if __name__ == "__main__":
    main()