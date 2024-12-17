
import os,sys

from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import ResourceNotFoundError

'''
创建Container
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
    storage_account_name = "leiteststorage666"
    #Azure存储账户所在数据中心区域，germanywestcentral就是Azure德国法兰克福
    location = "germanywestcentral"
    #container名称
    blobcontainer_name = "privatecontainer000"
    
    #自定义标签
    custom_tags = {
        'Environment': 'Development',
        'Department': 'IT'
    }
    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    # # For other authentication approaches, please see: https://pypi.org/project/azure-identity/
    resource_client = ResourceManagementClient(
        credential=clientcredential,
        subscription_id=subscription_id
    )
    storage_client = StorageManagementClient(
        credential=clientcredential,
        subscription_id=subscription_id
    )
    try:
      # Get storage account
      storage_account = storage_client.storage_accounts.get_properties(
            resourcegroup_name,
            storage_account_name
      )
    except ResourceNotFoundError:
      sys.exit(0)
    
    # Get blob container
    try:
      blob_container = storage_client.blob_containers.get(resourcegroup_name,storage_account_name,blobcontainer_name)
    except ResourceNotFoundError:
      print("Container not found. Try to create a new container\n")
      
      # Create blob container
      blob_container = storage_client.blob_containers.create(resourcegroup_name,storage_account_name,blobcontainer_name,{})
      print("Create blob container:\n{}".format(blob_container))

      # Get blob container
      blob_container = storage_client.blob_containers.get(
          resourcegroup_name,
          storage_account_name,
          blobcontainer_name
      )
      print("Get blob container:\n{}".format(blob_container))
      

      ###################################################################
      # 在存储账户级别，打开匿名访问功能
      # 请谨慎操作
      ###################################################################
      # storage_client.storage_accounts.update(
      #     resourcegroup_name,storage_account_name,
      #     {
      #       "allow_blob_public_access": True,
      #     }
      # )
      # print("Update storage account:\n{}".format(storage_account))


      ###################################################################
      # 把Container类型设置为Public，允许匿名访问
      # 请谨慎操作
      ###################################################################

      # Update blob container
      # blob_container = storage_client.blob_containers.update(
      #     resourcegroup_name,
      #     storage_account_name,
      #     blobcontainer_name,
      #     {
              
      #       "public_access": "Blob",
      #       "metadata": {
      #         "metadata": "true"
      #       }
      #     }
      # )
      # print("Update blob container:\n{}".format(blob_container))
       

if __name__ == "__main__":
    main()