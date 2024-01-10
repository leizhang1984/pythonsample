import time

from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

location = "germanywestcentral"
#sub_id_1 = "c69f7dec-22a1-4f72-a0b1-07811a7ed54b"
sub_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
rg_name= "sig-rg"
sig_name = "nio_image_template_fk"


network_client = NetworkManagementClient(
    credential = DefaultAzureCredential(),
    subscription_id = sub_id
)

compute_client = ComputeManagementClient(
    credential = DefaultAzureCredential(),
    subscription_id = sub_id
)


start_time = time.time()
images = compute_client.gallery_images.list_by_gallery(rg_name,sig_name)
for image in images:
    print(image.purchase_plan.publisher)
    print(image.purchase_plan.name)
    print(image.purchase_plan.product)

#print("--- %s seconds ---" % (time.time() - start_time))
#print("Created VM:\n{}".format(vm))

# For xfs use xfs_growfs /xxx
