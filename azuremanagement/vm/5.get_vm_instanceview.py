from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

location = "germanywestcentral"
#sub_id_1 = "c69f7dec-22a1-4f72-a0b1-07811a7ed54b"
sub_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
rg_name = "sig-rg"
#vm_name = "s-azeu3-mysqlmha-01"
vm_name = "NIO-EU-pv2-sample"


compute_client = ComputeManagementClient(
    credential = DefaultAzureCredential(),
    subscription_id = sub_id
)

vmstatus = compute_client.virtual_machines.instance_view(rg_name,vm_name)
# #当前操作的状态
# if vmstatus.statuses[0].code =="ProvisioningState/succeeded":

#     print(vmstatus.statuses[1].display_status)

# else:
#     print(vmstatus.statuses[0].display_status)

  # Get virtual machine
vm = compute_client.virtual_machines.get(
    rg_name,
    vm_name
)
#ppg = vm.proximity_placement_group;
#print("Get virtual machine:\n{}".format(ppg))

print("Get virtual machine:\n{}".format(vm))