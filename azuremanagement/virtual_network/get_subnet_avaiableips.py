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
    rg_name = "sig-rg"
    vnet_name = "NIO-EU"
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


    usages = network_client.virtual_networks.list_usage(rg_name,vnet_name)
    #遍历virtual network的所有子网
    for usage in usages:
        subnet_name = usage.id.split("subnets/")[1]
        subnet = network_client.subnets.get(rg_name,vnet_name,subnet_name)
        print("Subnet Name is:{}".format(subnet_name))
        print("Subnet Address Prefix is:{}".format(subnet.address_prefix))


        

    
if __name__ == "__main__":
    main()