from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

location = "westeurope"
#sub_id_1 = "c69f7dec-22a1-4f72-a0b1-07811a7ed54b"
sub_id_1 = "074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb"
rg_name_1 = "DEFAULTRG"
#vm_name = "s-azeu3-mysqlmha-01"
vm_name = "p-azeu2-azure-tod-nginx-ops-02"


compute_client = ComputeManagementClient(
    credential = DefaultAzureCredential(),
    subscription_id = sub_id_1
)



vmstatus = compute_client.virtual_machines.instance_view(rg_name_1,vm_name)
#当前操作的状态
if vmstatus.statuses[0].code =="ProvisioningState/succeeded":

    print(vmstatus.statuses[1].display_status)

else:
    print(vmstatus.statuses[0].display_status)
