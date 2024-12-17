
import os

from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.core.exceptions import ResourceNotFoundError

'''
创建存储账户
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
      #没找到该资源,则创建该资源
      storage_account = storage_client.storage_accounts.begin_create(
          resourcegroup_name,
          storage_account_name,
          {
            "sku": {
              "name": "Standard_LRS"
            },
            "kind": "StorageV2",
            "location": location,
            "encryption": {
              "services": {
                "file": {
                  "key_type": "Account",
                  "enabled": True
                },
                "blob": {
                  "key_type": "Account",
                  "enabled": True
                }
              },
              "key_source": "Microsoft.Storage"
            },
            "tags": custom_tags
          }
      ).result()
      print("Create storage account:\n{}".format(storage_account))

    
    #Update storage account
    storage_account = storage_client.storage_accounts.update(
        resourcegroup_name,
        storage_account_name,
        {
          "network_acls": {
            "default_action": "Allow"
          },
          "encryption": {
            "services": {
              "file": {
                "key_type": "Account",
                "enabled": True
              },
              "blob": {
                "key_type": "Account",
                "enabled": True
              }
            },
            "key_source": "Microsoft.Storage"
          },
          "tags": custom_tags
        }
    )
    print("Update storage account:\n{}".format(storage_account))
    
    # Delete storage account
    # storage_account = storage_client.storage_accounts.delete(
    #     GROUP_NAME,
    #     STORAGE_ACCOUNT
    # )
    # print("Delete storage account.\n")

    # Delete Group
    # resource_client.resource_groups.begin_delete(
    #     GROUP_NAME
    # ).result()


if __name__ == "__main__":
    main()