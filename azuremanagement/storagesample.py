from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

compute_client = ComputeManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id = "f0a0d925-df4f-4fcf-847c-9d9b746cf9e5"
)
disk = compute_client.disks.get(
    "test-rg",
    "dr0001-osdisk-20220716-001349"
)
print("Got disk:\n{}".format(disk))