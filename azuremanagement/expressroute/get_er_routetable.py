import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

tenantid = os.environ.get('tenantid')
clientid = os.environ.get('clientid')
clientsecret = os.environ.get('clientsecret')

def main():

    #订阅ID
    subid = "074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb"
    #资源组名称
    rg_name = "defaultrg"
    #专线名称
    ercircuit_name = "NIO-ER-FR01"
    #peering name
    peering_name = "AzurePrivatePeering"
    #device_path 1, ER是双线的，primary是第一根线路
    device_path1 = "Primary"

    #device_path 2, ER是双线的，Secondary是第一根线路
    device_path2 = "Secondary"

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    network_client = NetworkManagementClient(credential = clientcredential,subscription_id = subid)

    #第1根线路的的有效路由
    effective_route1  = network_client.express_route_circuits.begin_list_routes_table(rg_name,ercircuit_name,peering_name,device_path1).result()
    for route in effective_route1.value:
        print(f"Network: {route.network}, Next Hop: {route.next_hop}, Loc Prf: {route.loc_prf}, Weight: {route.weight}, Path: {route.path}")


    #第2根线路的的有效路由
    effective_route1  = network_client.express_route_circuits.begin_list_routes_table(rg_name,ercircuit_name,peering_name,device_path2).result()
    for route in effective_route1.value:
        print(f"Network: {route.network}, Next Hop: {route.next_hop}, Loc Prf: {route.loc_prf}, Weight: {route.weight}, Path: {route.path}")

if __name__ == '__main__':
    main()