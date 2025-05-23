'''
1.从镜像仓库创建虚拟机的脚本
'''
import os
import time

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

tenantid = os.environ.get('nonprod_tenantid')
clientid = os.environ.get('nonprod_clientid')
clientsecret = os.environ.get('nonprod_clientsecret')

location = "germanywestcentral"
#sub_id_1 = "c69f7dec-22a1-4f72-a0b1-07811a7ed54b"
sub_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
rg_name = "sig-rg"
vnet_name = "NIO-EU"
subnet_name = "PROD-EU-AZURE-TOD-FE-VM-01"
nic_name = "NIO-EU-Rocky9-01-nic"
public_ip_name = "NIO-EU-Rocky9-01-public-ip"
#创建的虚拟机名称
vm_name = "NIO-EU-Rocky9-01"
#计算机名称
computer_name = "NIO-EU-Rocky9-01"

vm_size = "Standard_D2s_v5" #dlsv5, esv5
#dsv5 1:4
#dlsv5 1:2
#esv5 1:8

#虚拟机可用区，只能设置1 或者2，或者3
availabiltiy_zone = "1"
#自定义标签
custom_tags = {
    'Environment': 'Development',
    'Department': 'IT'
}
#os_disk_sku = "Premium_LRS"
#操作系统盘只能是Premium_LRS和Standard_LRS
os_disk_sku = "Premium_LRS"
os_disk_name = vm_name + "-os-disk"
os_disk_size_gb = 100

#数据盘只能是Premium_LRS，Standard_LRS，PremiumV2_LRS
#标准HDD
#高级SSD
data_disk_sku = "Premium_LRS"
data_disk_name = vm_name + "-data-disk001"
data_disk_size_gb = 1024

sig_name = "nio_image_template_fk"
sig_img_name = "centos7.9"
sig_img_ver_name = "0.0.1"

#proximityPlacementGroups，请注意PPG保证多台虚拟机在同一个数据中心，相距的物理位置更近，但是不是高可用方案
#ppg_name="lei-ppg"

# Create client
clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)


network_client = NetworkManagementClient(
    credential = clientcredential,
    subscription_id = sub_id
)

compute_client = ComputeManagementClient(
    credential = clientcredential,
    subscription_id = sub_id
)

###先创建1个公网ip地址
start_time = time.time()
public_ip_parameters = {
    "location": location,
    "sku": {"name": "Standard"},
    "public_ip_allocation_method": "Static",
    "public_ip_address_version": "IPV4",
    "tags": custom_tags
}

public_ip = network_client.public_ip_addresses.begin_create_or_update(
    rg_name,
    public_ip_name,
    public_ip_parameters
).result()

###再创建1个网卡
nic = network_client.network_interfaces.begin_create_or_update(
    resource_group_name = rg_name,
    network_interface_name = nic_name,
    parameters = {
        "location": location,
        "ip_configurations": [{
            "name": "nic-ip-config",
            "subnet": {
                "id": "/subscriptions/" + sub_id + "/resourceGroups/" + rg_name + "/providers/Microsoft.Network/virtualNetworks/" + vnet_name + "/subnets/" + subnet_name
            },
        "public_ip_address": {
            "id": public_ip.id,
            "delete_option": "Delete",
        }
        }],
        "enable_accelerated_networking": True,

        "tags": custom_tags
    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Created NIC:\n{}".format(nic))

start_time = time.time()
vm = compute_client.virtual_machines.begin_create_or_update(
    resource_group_name = rg_name,
    vm_name = vm_name,
    parameters = {
        "location": location,
        #从get_gallery_image里获得的publisher,name, product，动态的填入下面的plan里
        #如果是ubuntu环境，则把plan内容全部去掉
        #如果是rocky 8环境，则不需要注释下面的环境，具体可以参考get_gallery_image.py
        #"plan": {
        #    "name": "free",
        #    "product": "rockylinux",
        #    "publisher": "erockyenterprisesoftwarefoundationinc1653071250513"
        #},
  
        "zones": [
            availabiltiy_zone
        ],
        "hardware_profile": {
            "vm_size": vm_size
        },
        "storage_profile": {
            "image_reference": {
                "id": "/subscriptions/" + sub_id + "/resourceGroups/" + rg_name + "/providers/Microsoft.Compute/galleries/" + sig_name + "/images/" + sig_img_name + "/versions/" + sig_img_ver_name
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
                "delete_option": "Delete",
                'tags': {
                    "creator": "Lei Zhang",
                    "organization": "MSFT"
                }
            },
            "data_disks": [
                {
                    "lun": 0,
                    "name": data_disk_name,
                    "caching": "None",  #"ReadOnly"
                    #如果是镜像不带datadisk，需要额外挂载新的、空的数据盘,创建的时候
                    #-必须指定lun, lun的值可以是0到63之间的任意值
                    #新挂载的data_disks, "create_option"为"Empty"

                    #如果是镜像带datadisk，如果要继承镜像里的data_disks里包含的数据，则创建的时候
                    #-必须指定lun, lun的值必须从之前镜像虚拟机里，拿到之前时候设置的值
                    #-"create_option"为"FromImage"
                    "create_option": "Empty",
                    "disk_size_gb": data_disk_size_gb,
                    
                    "managed_disk": {
                        "storage_account_type": data_disk_sku
                   },
                    "delete_option": "Delete",
                    'tags': {
                        "creator": "Lei Zhang",
                        "organization": "MSFT"
                    }
                }
            ]
        },
        "additional_capabilities": {
            #"ultra_ssd_enabled": True
            "ultra_ssd_enabled": False
        },
        "os_profile": {
            "computer_name": computer_name,
            "admin_username": "testuser",
            "admin_password": "abc@123456$%^&*"
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
        },
        # 请注意PPG保证多台虚拟机在同一个数据中心，相距的物理位置更近，但是不是高可用方案
        #'proximity_placement_group':{
        #    "id": "/subscriptions/" + sub_id + "/resourceGroups/" + rg_name + "/providers/Microsoft.Compute/proximityPlacementGroups/" + ppg_name

        #},
        'tags': {
            "creator": "Lei Zhang",
            "organization": "MSFT"
        }#,
        # "virtual_machine_scale_set": {
        #     "id": "/subscriptions/" + sub_id + "/resourceGroups/" + rg_name + "/providers/Microsoft.Compute/virtualMachineScaleSets/" + vmss_name
        # }
    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Created VM:\n{}".format(vm))

# For xfs use xfs_growfs /xxx
