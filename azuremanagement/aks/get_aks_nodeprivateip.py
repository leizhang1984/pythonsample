import os

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.containerservice import ContainerServiceClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient

tenantid = os.environ.get('tenantid')
clientid = os.environ.get('clientid')
clientsecret = os.environ.get('clientsecret')

subscription_id = '074b8f7e-9eb5-4c38-b5f9-a39cf7876bdb'
resource_group = 'default-rg'
aks_name = 'eu-aks-stg'

def main():
    #credential = DefaultAzureCredential()
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    aks_client = ContainerServiceClient(clientcredential, subscription_id)
    compute_client = ComputeManagementClient(clientcredential, subscription_id)
    network_client = NetworkManagementClient(clientcredential, subscription_id)

    aks_cluster = aks_client.managed_clusters.get(resource_group, aks_name)
    node_resource_group = aks_cluster.node_resource_group
    print(f'Node resource group: {node_resource_group}')
    print()

    node_pools = aks_client.agent_pools.list(resource_group, aks_name)
    for node_pool in node_pools:
        print(f'Node pool {node_pool.name} has {node_pool.count} nodes')

    print()

    vmss_list = compute_client.virtual_machine_scale_sets.list(node_resource_group)
    for vmss in vmss_list:
        print(f'VMSS {vmss.name} has {vmss.sku.capacity} nodes')

        vmss_vm_list = compute_client.virtual_machine_scale_set_vms.list(node_resource_group, vmss.name)
        for vmss_vm in vmss_vm_list:
            network_interface = network_client.network_interfaces.get_virtual_machine_scale_set_network_interface(node_resource_group, vmss.name, vmss_vm.instance_id, vmss_vm.network_profile.network_interfaces[0].id.split('/')[-1])
            private_ip = network_interface.ip_configurations[0].private_ip_address
            print(f'VMSS VM {vmss_vm.name} has private IP {private_ip}')

        print()
if __name__ == '__main__':
    main()