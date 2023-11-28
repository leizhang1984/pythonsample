from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

compute_client = ComputeManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id = "ffe7c7cd-f495-444a-9df7-9bcb39da2d66"
)

disk = compute_client.disks.get(
    "rg-test",
    "hdd-test"
)
print("Got disk:\n{}".format(disk))

compute_client.disks.begin_update(
    "rg-test",
    "hdd-test",
    {
        "tags": {
            "a": "1",
            "b": "2",
            "c": "3"
        }
    }
).result()
print("Updated disk:\n{}".format(disk))
