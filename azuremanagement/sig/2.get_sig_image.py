
import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    location = "germanywestcentral"
    #订阅ID
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    #资源组名称
    resource_group_name = "sig-rg"
    #gallery Name
    gallery_name = "nio_image_template_fk"

    #SIG Name最好以vmname-yyyymmdd 命名
    gallery_img_name = "centos8.2"
    gallery_img_ver_name = "0.0.1"

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    compute_client = ComputeManagementClient(
        clientcredential, subscription_id
    )


    images = compute_client.gallery_images.list_by_gallery(resource_group_name,gallery_name)
    for image in images:
        print(f"\nImage Name: {image.name}")
        print(f"Image Location: {image.location}")
        print(f"Image OS Type: {image.os_type}")
        
        # 获取共享镜像版本
        versions = compute_client.gallery_image_versions.list_by_gallery_image(resource_group_name, gallery_name, image.name)
        for version in versions:
            print(f"\n  Version Name: {version.name}")
            print(f"  Published Date: {version.publishing_profile.published_date}")
            
            # 获取操作系统磁盘和数据磁盘的容量
            os_disk_size = version.storage_profile.os_disk_image.size_in_gb
            print(f"  OS Disk Size: {os_disk_size} GB")
            
            data_disk_sizes = [disk.size_in_gb for disk in version.storage_profile.data_disk_images]
            print(f"  Data Disk Sizes: {data_disk_sizes} GB")


if __name__ == '__main__':
    main()