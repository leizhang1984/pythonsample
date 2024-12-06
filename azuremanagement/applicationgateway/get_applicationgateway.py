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
    rg_name = "FW-Hybrid-Test"
    applicationgateway_name = "leiappgw01"
    location = "germanywestcentral"

    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    network_client = NetworkManagementClient(
        credential=clientcredential,
        subscription_id=subscription_id
    )
    #获得7层负载均衡器
    application_gateway = network_client.application_gateways.get(rg_name,applicationgateway_name)
    print("Get load balancer:\n{}".format(application_gateway))


if __name__ == "__main__":
    main()