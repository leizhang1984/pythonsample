
import os

from azure.identity import DefaultAzureCredential, ClientSecretCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient

tenantid = os.environ.get('tenantid')
clientid = os.environ.get('clientid')
clientsecret = os.environ.get('clientsecret')

def main():
    
    subscriptionid = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    resourcegroupname = "test-rg"
    storageaccountname = "leiteststorage002"
    location = "germanywestcentral"
    #确保这个container提前创建好
    containername = "privatecontainer02"

    #默认值就是default，请不要修改
    lifecyclemanagement_policyname = "default"

    #rule name
    rulename = "rule01"

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    storage_client = StorageManagementClient(credential=clientcredential, subscription_id=subscriptionid)
    # Create management policy
    management_policy = storage_client.management_policies.create_or_update(
      resourcegroupname,
      storageaccountname,
      lifecyclemanagement_policyname,
      {
        "policy": {
          "rules": [
            {
              "enabled": True,
              "name": rulename,
              "type": "Lifecycle",
              "definition": {
                "filters": {
                  "blob_types": [
                    "blockBlob"
                  ],
                  "prefix_match": [
                    "olcmtestcontainer"
                  ]
                },
                "actions": {
                  "base_blob": {
                    "tier_to_cool": {
                      "days_after_modification_greater_than": "30"
                    },
                    "tier_to_archive": {
                      "days_after_modification_greater_than": "365"
                    },
                    "delete": {
                      "days_after_modification_greater_than": "1000"
                    }
                  },
                  "snapshot": {
                    "delete": {
                      "days_after_creation_greater_than": "180"
                    }
                  }
                }
              }
            }
          ]
        }
      }
  )
    print("Create management policy:\n{}".format(management_policy))
 
     # Get management policy
    management_policy = storage_client.management_policies.get(resourcegroupname,storageaccountname, lifecyclemanagement_policyname)
    print("Get management policy:\n{}".format(management_policy))

    
if __name__ == "__main__":
    main()