from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

#订阅ID
subid = "074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb"
#资源组名称
rg_name = "DEFAULTRG"
#虚拟机名称
vm_name = "p-azeu2-azure-tod-nginx-ops-02"

compute_client = ComputeManagementClient(credential = DefaultAzureCredential(),subscription_id = subid)

#网卡的资源ID
nicresourceid = compute_client.virtual_machines.get(rg_name,vm_name).network_profile.network_interfaces[0].id
print(nicresourceid)

#网卡名称
nicname = nicresourceid.split('/')[-1]
print(nicname)

network_client = NetworkManagementClient(credential = DefaultAzureCredential(),subscription_id = subid)

#网卡的有效路由
effective_route = network_client.network_interfaces.begin_get_effective_route_table(rg_name,nicname).result()
for route in effective_route.value:
    print(route)