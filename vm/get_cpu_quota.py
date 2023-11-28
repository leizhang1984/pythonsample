from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

compute_client = ComputeManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id = "074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb"
)

usage_list = compute_client.usage.list("westeurope")
for usage in usage_list:
    print(usage.as_dict())