import os

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resourcegraph import ResourceGraphClient

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
    #获得7层负载均衡器，后端服务器健康状况
    application_gateway_backend_health = network_client.application_gateways.begin_backend_health(rg_name,applicationgateway_name).result()
   
    for backend_pool in application_gateway_backend_health.backend_address_pools:
        print(f"Backend pool ID: {backend_pool.backend_address_pool.id}")
        for http_settings in backend_pool.backend_http_settings_collection:
            for server in http_settings.servers:
                print(f"Server address: {server.address}, Health: {server.health}")

if __name__ == "__main__":
    main()