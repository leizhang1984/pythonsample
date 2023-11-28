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
images = compute_client.gallery_images.list_by_gallery(rg_name_1,sig_name)
for image in images:
    print(image.purchase_plan.publisher)
    print(image.purchase_plan.name)
    print(image.purchase_plan.product)

#print("--- %s seconds ---" % (time.time() - start_time))
#print("Created VM:\n{}".format(vm))

# For xfs use xfs_growfs /xxx
