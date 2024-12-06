import time

from azure.identity import DefaultAzureCredential
from azure.mgmt.compute import ComputeManagementClient

location = "germanywestcentral"
sub_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
rg_name = "sig-rg"
vm_name = "unbubtutest01"
#Restore Point Collection 最好以vmname-yyyymmdd 命名
rpc_name = "lei-rpc02"
#restore point 最好以最好以vmname-rp-yyymmdd 命名
rp_name = "20230105"

#sub_id_2 = "f0a0d925-df4f-4fcf-847c-9d9b746cf9e5"
#rg_name_2 = "max-rg"
sig_name = "nio_image_template_fk"

#SIG Name最好以vmname-yyyymmdd 命名
sig_img_name = "lei-sig-img"
sig_img_pub = "lei-pub"
sig_img_offer = "lei-offer"
sig_img_sku = "lei-sku"
sig_img_ver_name = "0.0.1"

compute_client = ComputeManagementClient(
    credential = DefaultAzureCredential(),
    subscription_id = sub_id
)

#compute_client_2 = ComputeManagementClient(
#    credential = DefaultAzureCredential(),
#    subscription_id = sub_id_2
#)

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
print("Created RPC:\n{}".format(rpc))

start_time = time.time()
rp = compute_client.restore_points.begin_create(
    resource_group_name = rg_name,
    restore_point_collection_name = rpc_name,
    restore_point_name = rp_name,
    parameters = {

    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Created RP:\n{}".format(rp))

rp_os_disk = rp.source_metadata.storage_profile.os_disk
#print("RP OS Disk " +rp_os_disk)
os_disk_name = rp_os_disk.name + "-" + rp.name
#print("OS Disk Name " + os_disk_name)
rp_data_disk = rp.source_metadata.storage_profile.data_disks[0]
#print("RP Data Disk " + rp_data_disk)
data_disk_name = rp_data_disk.name + "-" + rp.name
#print("RP Data Disk Name " + data_disk_name)

start_time = time.time()
os_disk = compute_client.disks.begin_create_or_update(
    resource_group_name = rg_name,
    disk_name = os_disk_name,
    disk = {
        "location": location,
        "creation_data": {
            "create_option": "Restore",
            "source_resource_id": rp_os_disk.disk_restore_point.id
        }
    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Created OS disk:\n{}".format(os_disk))

start_time = time.time()
data_disk = compute_client.disks.begin_create_or_update(
    resource_group_name = rg_name,
    disk_name = data_disk_name,
    disk = {
        "location": location,
        "creation_data": {
            "create_option": "Restore",
            "source_resource_id": rp_data_disk.disk_restore_point.id
        }
    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Created data disk:\n{}".format(data_disk))

start_time = time.time()
sig = compute_client.galleries.begin_create_or_update(
    resource_group_name = rg_name,
    gallery_name = sig_name,
    gallery = {
        "location": location
    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Created SIG:\n{}".format(sig))

start_time = time.time()
sig_img = compute_client.gallery_images.begin_create_or_update(
    resource_group_name = rg_name,
    gallery_name = sig_name,
    gallery_image_name = sig_img_name,
    gallery_image = {
        "location": location,
        "os_type": "Linux",
        "os_state": "Generalized",
        "hyper_v_generation": "V2",
        "IsAcceleratedNetworkSupported": "false",
        "identifier": {
            "publisher": sig_img_pub,
            "offer": sig_img_offer,
            "sku": sig_img_sku
        },
        "features": [
        {
            "name": "SecurityType",
            "value": "TrustedLaunch"
        }
        ]
    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Created SIG image:\n{}".format(sig_img))

start_time = time.time()
sig_img_ver = compute_client.gallery_image_versions.begin_create_or_update(
    resource_group_name = rg_name,
    gallery_name = sig_name,
    gallery_image_name = sig_img_name,
    gallery_image_version_name = sig_img_ver_name,
    gallery_image_version = {
        "location": location,
        "publishing_profile": {
            "target_regions": [
                {
                    "name": location,
                    "regional_replica_count": 1, # If replication_mode equals Shallow, the value can only be 1. If replication_mode equals Full, the value can be 1 to 100.
                    "storage_account_type": "Standard_LRS"
                }
            ],
            "replication_mode": "Shallow" # Shallow/Full
        },
        "storage_profile": {
            "os_disk_image": {
                "host_caching": "None",
                "source": {
                    "id": os_disk.id
                }
            },
            "data_disk_images": [
                {
                    "lun": 0,
                    "host_caching": "None",
                    "source": {
                        "id": data_disk.id
                    }
                }
            ]
        }
    }
).result()
print("--- %s seconds ---" % (time.time() - start_time))
print("Created SIG image version:\n{}".format(sig_img_ver))


##删除OS磁盘
compute_client.disks.begin_delete(resource_group_name = rg_name,
    disk_name = os_disk_name)
print("delete os disk complete")

##删除Data Disk
compute_client.disks.begin_delete(resource_group_name = rg_name,
    disk_name = data_disk_name)
print("delete data disk complete")