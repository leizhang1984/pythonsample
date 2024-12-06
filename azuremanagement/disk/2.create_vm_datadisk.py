import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import DiskCreateOption, DiskSku, StorageAccountTypes

def main():

    location = "germanywestcentral"
    subscription_id = "b5aa1700-1510-4f35-b134-fe9c7c695df1"
    rg_name = "aks-rg"
    diskname = "centos82-datadisk02"


    tenantid = ""
    clientid = ""
    clientsecret = ""
    
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    compute_client = ComputeManagementClient(credential = clientcredential, subscription_id = subscription_id)

    response = compute_client.disks.begin_create_or_update(rg_name, diskname,
             {
                "location": location,
                "sku": DiskSku(name=StorageAccountTypes.PREMIUM_V2_LRS),
                "disk_size_gb": 1023,
                "zones": ['1'],
                "disk_iops_read_write": 3000,
                "disk_m_bps_read_write": 125,
                "network_access_policy": "DenyAll",
                'creation_data': {
                    'create_option': DiskCreateOption.EMPTY
                },
            }
    ).result()

    print(response)

if __name__ == '__main__':
    main()