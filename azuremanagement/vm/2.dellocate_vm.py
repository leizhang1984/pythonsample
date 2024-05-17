from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

sub_id_1 = "166157a8-9ce9-400b-91c7-1d42482b83d6"

compute_client = ComputeManagementClient(
    credential = DefaultAzureCredential(),
    subscription_id = sub_id_1
)

vm = compute_client.virtual_machines.begin_deallocate("rg-test", "vm-test").wait()
print("Deallocated virtual machine.")

vm = compute_client.virtual_machines.begin_delete("rg-test", "vm-test", force_deletion=True).wait()
print("Deleted virtual machine.")
