
import os

from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.storage.blob import BlobServiceClient
from azure.core.exceptions import ResourceNotFoundError


'''
统计存储账户的container容量
'''
def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    #订阅名称
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    #资源组名称
    resourcegroup_name = "test-rg"
    #存储账户名称
    storage_account_name = "leiteststorage000"
    #Azure存储账户所在数据中心区域，germanywestcentral就是Azure德国法兰克福
    location = "germanywestcentral"

     # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    # # For other authentication approaches, please see: https://pypi.org/project/azure-identity/
    resource_client = ResourceManagementClient(clientcredential, subscription_id)

    storage_client = StorageManagementClient(clientcredential, subscription_id)
    try:
      # Get storage account
      storage_account = storage_client.storage_accounts.get_properties(resourcegroup_name,storage_account_name)

      account_url = "https://" + storage_account_name + ".blob.core.windows.net"

      blob_service_client = BlobServiceClient(account_url, credential = clientcredential)

      containers = blob_service_client.list_containers()
      #遍历所有容器
      for container in containers:
         #显示container name
         print(container.name)
         container_client = blob_service_client.get_container_client(container.name)
         #遍历所有Blob
         blobs = container_client.list_blobs()
         for blob in blobs:
            #显示文件名
            print(blob.name)

    except ResourceNotFoundError:
      #没找到该资源

      print("Can not find this storage Account")

    
    #Update storage account
    


if __name__ == "__main__":
    main()