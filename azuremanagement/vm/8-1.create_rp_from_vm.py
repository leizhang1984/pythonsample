#####################################
###基于虚拟机OS Disk + Data Disk，做快照
###快照保存到Azure Restore Point Collection集合里
###成为一个单独的restore point
###后续根据这个Restore Point创建新的虚拟机即可


import time, json

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

sub_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
location = "germanywestcentral"
rg_name = "sig-rg"
vm_name = "NIO-EU-Hadoop-01" # VM info: zone 1, Standard_D2s_v5, OS disk: 30GB HDD, data disk: 100GB HDD
rpc_name = "lei-rpc-20240307-1727"
rp_name = "lei-rp01-2-240307-1727"

compute_client = ComputeManagementClient(
    credential = DefaultAzureCredential(),
    subscription_id = sub_id
)

start_time = time.time()
rpc = compute_client.restore_point_collections.create_or_update(
    resource_group_name = rg_name,
    restore_point_collection_name = rpc_name,
    parameters = {
        "location": location,
        "source": {
            "id": "/subscriptions/" + sub_id + "/resourceGroups/" + rg_name + "/providers/Microsoft.Compute/virtualMachines/" + vm_name
        }
    }
)
print("--- %s seconds ---" % (time.time() - start_time))
print("Created RPC:\n{}".format(json.dumps(rpc.as_dict())))

start_time = time.time()
rp = compute_client.restore_points.begin_create(
    resource_group_name = rg_name,
    restore_point_collection_name = rpc_name,
    restore_point_name = rp_name,
    parameters = {

    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Created RP:\n{}".format(json.dumps(rp.as_dict())))

data_disk_rp_id = rp.source_metadata.storage_profile.data_disks[0].disk_restore_point.id
data_disk_rp_name = data_disk_rp_id[data_disk_rp_id.rindex("/") + 1:]
print("Data disk RP name: {}".format(data_disk_rp_name))

data_disk_rp_completion_percent = float(0.0)
while data_disk_rp_completion_percent < 100.0:
    start_time = time.time()
    data_disk_rp = compute_client.disk_restore_point.get(
        resource_group_name = rg_name,
        restore_point_collection_name = rpc_name,
        vm_restore_point_name = rp_name,
        disk_restore_point_name = data_disk_rp_name
    )

    #如果是HDD 磁盘，data_disk_rp.completion_percent 默认为Null
    if data_disk_rp.completion_percent == None:
        data_disk_rp_completion_percent = 100.0
        break
    else:
        data_disk_rp_completion_percent = data_disk_rp.completion_percent

    print("--- %s seconds ---" % (time.time() - start_time))
    print("Data disk RP completion percent: {}".format(data_disk_rp_completion_percent))
    time.sleep(5)

print("Data disk RP is 100% completed.")
