
import os

from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient


def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    SUBSCRIPTION_ID = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    GROUP_NAME = "test-rg"
    STORAGE_ACCOUNT = "leiteststorage001"
    location = "germanywestcentral"

    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    # # For other authentication approaches, please see: https://pypi.org/project/azure-identity/
    resource_client = ResourceManagementClient(
        credential=clientcredential,
        subscription_id=SUBSCRIPTION_ID
    )
    storage_client = StorageManagementClient(
        credential=clientcredential,
        subscription_id=SUBSCRIPTION_ID
    )

    # Create resource group
    # resource_client.resource_groups.create_or_update(
    #     GROUP_NAME,
    #     {"location": "eastus"}
    # )

    # Create storage account
    storage_account = storage_client.storage_accounts.begin_create(
        GROUP_NAME,
        STORAGE_ACCOUNT,
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
          "tags": {
            "key1": "value1",
            "key2": "value2"
          }
        }
    ).result()
    print("Create storage account:\n{}".format(storage_account))

    # Get storage account
    storage_account = storage_client.storage_accounts.get_properties(
        GROUP_NAME,
        STORAGE_ACCOUNT
    )
    print("Get storage account:\n{}".format(storage_account))

    # Update storage account
    # storage_account = storage_client.storage_accounts.update(
    #     GROUP_NAME,
    #     STORAGE_ACCOUNT,
    #     {
    #       "network_acls": {
    #         "default_action": "Allow"
    #       },
    #       "encryption": {
    #         "services": {
    #           "file": {
    #             "key_type": "Account",
    #             "enabled": True
    #           },
    #           "blob": {
    #             "key_type": "Account",
    #             "enabled": True
    #           }
    #         },
    #         "key_source": "Microsoft.Storage"
    #       }
    #     }
    # )
    # print("Update storage account:\n{}".format(storage_account))
    
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