import time,os,sys

from azure.identity import ClientSecretCredential
from azure.mgmt.quota import QuotaMgmtClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.machinelearningservices import AzureMachineLearningWorkspaces


'''
Azure Machine Learning
'''
def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    #Azure数据中心区域
    #location = "germanywestcentral"
    location = "swedencentral"

    #Azure订阅ID
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    #compute_client = ComputeManagementClient(clientcredential, subscription_id)
    ml_client = AzureMachineLearningWorkspaces(clientcredential, subscription_id)

    print("Listing all Azure Machine Learning SKUs:")
    aml_computes = ml_client.virtual_machine_sizes.list(location).aml_compute
    for aml_compute in aml_computes:
        print(f"Name: {aml_compute.name}, Family: {aml_compute.family}, CPU: {aml_compute.v_cp_us}, GPU: {aml_compute.gpus}")
        
    # for vm_sku in compute_client.virtual_machine_sizes.list(location):
    #     print(f"Name: {vm_sku.name}, Number of Cores: {vm_sku.number_of_cores}, Memory (MB): {vm_sku.memory_in_mb}")
    #result= ml_client.list_skus
   
    #    print(f"Name: {sku.name}, Tier: {sku.tier}, Kind: {sku.kind}")
    

if __name__ == '__main__':
    main()
