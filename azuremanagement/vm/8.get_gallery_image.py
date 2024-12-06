import time

from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

location = "germanywestcentral"
sub_id = "074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb"
#sub_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
rg_name= "defaultrg"
#rg_name= "sig-rg"

sig_name = "nio_image_template_fk"


network_client = NetworkManagementClient(
    credential = DefaultAzureCredential(),
    subscription_id = sub_id
)

compute_client = ComputeManagementClient(
    credential = DefaultAzureCredential(),
    subscription_id = sub_id
)


# start_time = time.time()
# images = compute_client.gallery_images.list_by_gallery(rg_name,sig_name)
# for image in images:
#     print(image.name)
#     if image.purchase_plan is not None:
#         print(image.purchase_plan.publisher)
#         print(image.purchase_plan.name)
#         print(image.purchase_plan.product)

images2 = compute_client.gallery_images.get(rg_name,sig_name,"dd_tod_lb_rocky8")
print(images2.purchase_plan.publisher)
print(images2.purchase_plan.name)
print(images2.purchase_plan.product)

#print("--- %s seconds ---" % (time.time() - start_time))
#print("Created VM:\n{}".format(vm))

# For xfs use xfs_growfs /xxx
