import time

from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

location = "westeurope"
#sub_id_1 = "c69f7dec-22a1-4f72-a0b1-07811a7ed54b"
sub_id_1 = "166157a8-9ce9-400b-91c7-1d42482b83d6"
rg_name_1 = "nio-rg"
vnet_name = "nio-vnet"
snet_name = "subnet-1"
nic_name = "lei-nic"
vmss_name = "lei-vmss"
vm_name = "lei-vm"
vm_size = "Standard_B2als_v2"
os_disk_name = vm_name + "-os-disk"
os_disk_size_gb = 100
os_disk_sku = "Premium_LRS"
data_disk_name = vm_name + "-data-disk"
data_disk_size_gb = 8192
data_disk_sku = "Premium_LRS"

sub_id_2 = "166157a8-9ce9-400b-91c7-1d42482b83d6"
rg_name_2 = "nio-rg"
sig_name = "gallery01"
sig_img_name = "rocky8"
sig_img_ver_name = "0.0.1"

network_client = NetworkManagementClient(
    credential = DefaultAzureCredential(),
    subscription_id = sub_id_1
)

compute_client = ComputeManagementClient(
    credential = DefaultAzureCredential(),
    subscription_id = sub_id_1
)

start_time = time.time()
nic = network_client.network_interfaces.begin_create_or_update(
    resource_group_name = rg_name_1,
    network_interface_name = nic_name,
    parameters = {
        "location": location,
        "ip_configurations": [{
            "name": "nic-ip-config",
            "subnet": {
                "id": "/subscriptions/" + sub_id_1 + "/resourceGroups/" + rg_name_1 + "/providers/Microsoft.Network/virtualNetworks/" + vnet_name + "/subnets/" + snet_name
            }
        }],
        "enable_accelerated_networking": True
    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Created NIC:\n{}".format(nic))

start_time = time.time()
vm = compute_client.virtual_machines.begin_create_or_update(
    resource_group_name = rg_name_1,
    vm_name = vm_name,
    parameters = {
        "location": location,
        "plan": {
            "name": "free",
            "product": "rockylinux",
            "publisher": "erockyenterprisesoftwarefoundationinc1653071250513"
        },
        "zones": [
            "1"
        ],
        "hardware_profile": {
            "vm_size": vm_size
        },
        "storage_profile": {
            "image_reference": {
                "id": "/subscriptions/" + sub_id_2 + "/resourceGroups/" + rg_name_2 + "/providers/Microsoft.Compute/galleries/" + sig_name + "/images/" + sig_img_name + "/versions/" + sig_img_ver_name
            },
            "os_disk": {
                "os_type": "Linux",
                "name": os_disk_name,
                "caching": "None",
                "create_option": "FromImage",
                "disk_size_gb": os_disk_size_gb,
                "managed_disk": {
                    "storage_account_type": os_disk_sku
                },
                "delete_option": "Delete"
            }#,
            #"data_disks": [
            #    {
            #        "lun": 0,
            #        "name": data_disk_name,
            #        "caching": "None",
            #        "create_option": "FromImage",
            #        "disk_size_gb": data_disk_size_gb,
            #        "managed_disk": {
            #            "storage_account_type": data_disk_sku
            #       },
            #        "delete_option": "Delete"
            #    }
            #]
        },
        "additional_capabilities": {
            "ultra_ssd_enabled": True
        },
        "os_profile": {
            "computer_name": "test-computer.abc.com",
            "admin_username": "testuser",
            "admin_password": "abc@123456$%^&*"
        },
        "network_profile": {
            "network_interfaces": [
                {
                    "id": "/subscriptions/" + sub_id_1 + "/resourceGroups/" + rg_name_1 + "/providers/Microsoft.Network/networkInterfaces/" + nic_name,
                    "primary": True,
                    "enableAcceleratedNetworking": True,
                    "delete_option": "Delete"
                }
            ]
        },
        "diagnostics_profile": {
            "boot_diagnostics": {
                "enabled": True
            }
        }#,
        #"virtual_machine_scale_set": {
        #    "id": "/subscriptions/" + sub_id_1 + "/resourceGroups/" + rg_name_1 + "/providers/Microsoft.Compute/virtualMachineScaleSets/" + vmss_name
        #}
    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Created VM:\n{}".format(vm))

# For xfs use xfs_growfs /xxx
