import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient

location = "germanywestcentral"
#sub_id_1 = "c69f7dec-22a1-4f72-a0b1-07811a7ed54b"
subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
rg_name = "aks-rg"
#vm_name = "s-azeu3-mysqlmha-01"
vm_name = "centos8.2"

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')
    
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    compute_client = ComputeManagementClient(credential = clientcredential, subscription_id = subscription_id)
  

    vm = compute_client.virtual_machines.get(rg_name,vm_name)
    #os disk name
    osdiskname = vm.storage_profile.os_disk.name

    osdiskinfo = compute_client.disks.get(rg_name, osdiskname)

    print("Get Disk Info:\n{}".format(osdiskinfo))

if __name__ == '__main__':
    main()