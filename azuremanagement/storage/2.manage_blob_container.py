
import os

from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient

tenantid = os.environ.get('tenantid')
clientid = os.environ.get('clientid')
clientsecret = os.environ.get('clientsecret')

def main():

    SUBSCRIPTION_ID = "b5aa1700-1510-4f35-b134-fe9c7c695df1"
    GROUP_NAME = "test-rg"
    STORAGE_ACCOUNT = "leizhangstorage00"
    location = "germanywestcentral"
    blobcontainer_name = "privatecontainer"

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
    '''
    storage_account = storage_client.storage_accounts.begin_create(
        GROUP_NAME,
        STORAGE_ACCOUNT,
        {
          "sku": {
            "name": "Standard_LRS"
          },
          "kind": "StorageV2",
          "location": location,
          "allow_blob_public_access": False,
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

 
   # Create blob container
    blob_container = storage_client.blob_containers.create(
        GROUP_NAME,
        STORAGE_ACCOUNT,
        blobcontainer_name,
        {}
    )
    print("Create blob container:\n{}".format(blob_container))
    '''
    
    # Get blob container
    blob_container = storage_client.blob_containers.get(
        GROUP_NAME,
        STORAGE_ACCOUNT,
        blobcontainer_name
    )
    print("Get blob container:\n{}".format(blob_container))
    

    # Allow Blob anonymous access = Enable
    storage_client.storage_accounts.update(
        GROUP_NAME,STORAGE_ACCOUNT,
        {
          "allow_blob_public_access": True,
        }
    )
    print("Update storage account:\n{}".format(storage_account))


    ###################################################################
    ###################################################################
    ###################################################################

      # Update blob container
    blob_container = storage_client.blob_containers.update(
        GROUP_NAME,
        STORAGE_ACCOUNT,
        blobcontainer_name,
        {
            
          "public_access": "Blob",
          "metadata": {
            "metadata": "true"
          }
        }
    )
    print("Update blob container:\n{}".format(blob_container))


if __name__ == "__main__":
    main()