from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient


rg_name = "MC_default-rg_eu-aks-stg_westeurope"
vmssname = "aks-default-27052504-vmss"

compute_client = ComputeManagementClient(
 credential=DefaultAzureCredential(),
 subscription_id = "074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb"
)

networkclient = NetworkManagementClient(credential=DefaultAzureCredential(), subscription_id = "074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb")

vmsslists = compute_client.virtual_machine_scale_sets.list(rg_name)

for vmsslist in vmsslists:
  print(vmsslist.name)
  
vmssname = networkclient.network_interfaces.get_virtual_machine_scale_set_ip_configuration(rg_name,vmssname,"0","aks-default-27052504-vmss","ipconfig1")
print(vmssname)




#ipconfig = networkclient.(rg_name,vmssname,"0")
#print(ipconfig)