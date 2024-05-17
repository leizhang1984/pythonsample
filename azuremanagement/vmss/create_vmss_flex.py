import time

from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

location = "germanywestcentral"
sub_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
rg_name = "sig-rg"
vnet_name = "sig-vnet"
subnet_name = "subnet-1"
vmss_name = "test-vmss"
vm_size = "Standard_D2s_v5"

compute_client = ComputeManagementClient(
    credential= DefaultAzureCredential(),
    subscription_id = sub_id
)

start_time = time.time()
vmss = compute_client.virtual_machine_scale_sets.begin_create_or_update(
    resource_group_name = rg_name,
    vm_scale_set_name = vmss_name,
    parameters = {
        "location": location,
        "zones": [
            "1"
        ],
        "sku": {
            "name": vm_size,
            "tier": "Standard",
            #capacity 说明VMSS的虚拟机数量
            "capacity": 10
        },
        #如果只在1个可用区AZ里部署，platform_fault_domain_count只能设置为1
        #如果跨可用区，platform_fault_domain_count可以设置为5
        "platform_fault_domain_count": 1,
        "orchestration_mode": "Flexible",
        "virtual_machine_profile": {
            "os_profile": {
                "computer_name_prefix": "test-computer",
                "admin_username": "azureadmin",
                "admin_password": "$MgV#3*JKbs111222333"
            },
            "storage_profile": {
                "image_reference": {
                    "publisher": "OpenLogic",
                    "offer": "CentOS",
                    "sku": "7_9-gen2",
                    "version": "latest"
                },
                "os_disk": {
                    "os_type": "Linux",
                    "create_option": "FromImage",
                    "delete_option": "Delete"
                }
            },
            "network_profile": {
                "network_api_version": "2020-11-01",
                "network_interface_configurations": [
                    {
                        "name": "nic-ip-config",
                        "primary": True,
                        "enable_accelerated_networking": True,
                        "deleteOption": "Delete",
                        "ip_configurations": [{
                            "name": "nic-ip-config",
                            "subnet": {
                                "id": "/subscriptions/" + sub_id + "/resourceGroups/" + rg_name + "/providers/Microsoft.Network/virtualNetworks/" + vnet_name + "/subnets/" + subnet_name
                            }
                        }]
                    }
                ]
            },
            "diagnostics_profile": {
                "boot_diagnostics": {
                    "enabled": True
                }
            }
        }
    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Created VMSS:\n{}".format(vmss))
