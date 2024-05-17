import time

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

location = "germanywestcentral"
sub_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
rg_name = "sig-rg"
ppg_name = 'lei-ppg'

compute_client = ComputeManagementClient(
    credential = DefaultAzureCredential(),
    subscription_id = sub_id
)

#Create proximity placement group
proximity_placement_group = compute_client.proximity_placement_groups.create_or_update(
    rg_name,
    ppg_name,
    {
        "location": location,
        "proximity_placement_group_type": "Standard"
    }
)

print("Created PPG Completed")
# Get proximity placement group
proximity_placement_group = compute_client.proximity_placement_groups.get(
    rg_name,
    ppg_name
)
print("Get proximity placement group:\n{}".format(proximity_placement_group))