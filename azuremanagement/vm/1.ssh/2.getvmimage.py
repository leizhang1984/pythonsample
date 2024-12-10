'''
从镜像仓库创建虚拟机的脚本
创建的时候会在网卡上绑定安全组
'''
import os
import time
import sys

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient


tenantid = os.environ.get('nonprod_tenantid')
clientid = os.environ.get('nonprod_clientid')
clientsecret = os.environ.get('nonprod_clientsecret')

#订阅ID
sub_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"

# Create client
clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)


# 创建 ComputeManagementClient
compute_client = ComputeManagementClient(clientcredential, sub_id)

# 列出所有可用的镜像发布者
#Azure数据中心
location = "germanywestcentral"

#具体可以参考：
#https://az-vm-image.info/?cmd=--all+--publisher+OpenLogic

# publishers = compute_client.virtual_machine_images.list_publishers(location)
# for publisher in publishers:
#     print(f"Publisher: {publisher.name}")

# Centos的publisher 是OpenLogic
publisher_name = 'OpenLogic' 
offers = compute_client.virtual_machine_images.list_offers(location, publisher_name)
for offer in offers:
    print(f"Offer: {offer.name}")

# 列出特定发布者和镜像的 SKU
offer_name = 'CentOS'  # 替换为你感兴趣的镜像
skus = compute_client.virtual_machine_images.list_skus(location, publisher_name, offer_name)
for sku in skus:
    print(f"SKU: {sku.name}")

# 列出特定 SKU 的镜像版本
sku_name = '7_8-gen2'  # 替换为你感兴趣的 SKU
versions = compute_client.virtual_machine_images.list(location, publisher_name, offer_name, sku_name)
for version in versions:
    print(f"Version: {version.name}")
