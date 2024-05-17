import time, json

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient

sub_id = "c69f7dec-22a1-4f72-a0b1-07811a7ed54b"
location = "westus3"
zone = "2"
rg_name = "rpcv2-rg"
rpc_name = "test-rpc"
rp_name = "test-rp"
vm_name = "new-vm" # VM info: zone 2, Standard_D4s_v5, OS disk: 100GB Prem SSD, data disk: 2TB Ultra SSD
vm_size = "Standard_D4s_v5"
os_disk_name = vm_name + "-os-disk"
os_disk_size_gb = 100
os_disk_sku = "Premium_LRS"
data_disk_name = vm_name + "-data-disk"
data_disk_size_gb = 2048
data_disk_sku = "UltraSSD_LRS"
data_disk_iops = 2048
data_disk_mbps = 20
vnet_name = "test-vnet"
snet_name = "default"
nic_name = "test-nic"

compute_client = ComputeManagementClient(
    credential = DefaultAzureCredential(),
    subscription_id = sub_id
)

network_client = NetworkManagementClient(
    credential=DefaultAzureCredential(),
    subscription_id = sub_id
)

rp = compute_client.restore_points.get(
    resource_group_name = rg_name,
    restore_point_collection_name = rpc_name,
    restore_point_name = rp_name
)
print("Got RP:\n{}".format(json.dumps(rp.as_dict())))

start_time = time.time()
os_disk = compute_client.disks.begin_create_or_update(
    resource_group_name = rg_name,
    disk_name = os_disk_name,
    disk = {
        "location": location,
        "zones": [
            zone
        ],
        "sku": {
            "name": os_disk_sku
        },
        "creation_data": {
            "create_option": "Restore",
            "source_resource_id": rp.source_metadata.storage_profile.os_disk.disk_restore_point.id
        },
        "disk_size_gb": os_disk_size_gb
    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Restored OS disk:\n{}".format(json.dumps(os_disk.as_dict())))

start_time = time.time()
data_disk = compute_client.disks.begin_create_or_update(
    resource_group_name = rg_name,
    disk_name = data_disk_name,
    disk = {
        "location": location,
        "zones": [
            zone
        ],
        "sku": {
            "name": data_disk_sku
        },
        "creation_data": {
            "create_option": "Restore",
            "source_resource_id": rp.source_metadata.storage_profile.data_disks[0].disk_restore_point.id,
            "logical_sector_size": 512
        },
        "disk_size_gb": data_disk_size_gb,
        "disk_iops_read_write": data_disk_iops,
        "disk_m_bps_read_write": data_disk_mbps
    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Restored data disk:\n{}".format(json.dumps(data_disk.as_dict())))

# data_disk_completion_percent = 0.0
# while data_disk_completion_percent < 100.0:
#     start_time = time.time()
#     data_disk = compute_client.disks.get(
#         resource_group_name = rg_name,
#         disk_name = data_disk_name
#     )
#     data_disk_completion_percent = data_disk.completion_percent
#     print("--- %s seconds ---" % (time.time() - start_time))
#     print("Data disk completion percent: {}".format(data_disk_completion_percent))
#     time.sleep(5)
# print("Data disk is 100% completed.")

start_time = time.time()
nic = network_client.network_interfaces.begin_create_or_update(
    resource_group_name = rg_name,
    network_interface_name = nic_name,
    parameters = {
        "location": location,
        "ip_configurations": [{
            "name": "nic-ip-config",
            "subnet": {
                "id": "/subscriptions/" + sub_id + "/resourceGroups/" + rg_name + "/providers/Microsoft.Network/virtualNetworks/" + vnet_name + "/subnets/" + snet_name
            }
        }],
        "enable_accelerated_networking": True
    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Created NIC:\n{}".format(json.dumps(nic.as_dict())))

start_time = time.time()
vm = compute_client.virtual_machines.begin_create_or_update(
    resource_group_name = rg_name,
    vm_name = vm_name,
    parameters = {
        "location": location,
        "zones": [
            zone
        ],
        "hardware_profile": {
            "vm_size": vm_size
        },
        "storage_profile": {
            "os_disk": {
                "os_type": "Linux",
                "name": os_disk_name,
                "caching": "None",
                "create_option": "Attach",
                "managed_disk": {
                    "id": "/subscriptions/" + sub_id + "/resourcegroups/" + rg_name + "/providers/Microsoft.Compute/disks/" + os_disk_name
                },
                "delete_option": "Delete"
            },
            "data_disks": [
                {
                    "lun": 0,
                    "name": data_disk_name,
                    "caching": "None",
                    "create_option": "Attach",
                    "managed_disk": {
                        "id": "/subscriptions/" + sub_id + "/resourcegroups/" + rg_name + "/providers/Microsoft.Compute/disks/" + data_disk_name
                    },
                    "delete_option": "Delete"
                }
            ]
        },
        "additional_capabilities": {
            "ultra_ssd_enabled": True
        },
        "network_profile": {
            "network_interfaces": [
                {
                    "id": "/subscriptions/" + sub_id + "/resourceGroups/" + rg_name + "/providers/Microsoft.Network/networkInterfaces/" + nic_name,
                    "primary": True,
                    "delete_option": "Delete"
                }
            ]
        },
        "diagnostics_profile": {
            "boot_diagnostics": {
                "enabled": True
            }
        }
    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Created VM:\n{}".format(json.dumps(vm.as_dict())))
