import os

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    rg_name = "sig-rg"
    #第一个负载均衡器
    loadbalacer_name = "NIO-EU-Hadoop-VMSS-2LB"
    #第二个负载均衡器
    loadbalacer_name_2= "NIO-EU-Hadoop-VMSS-2LB-02"
    location = "germanywestcentral"

    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    network_client = NetworkManagementClient(
        credential=clientcredential,
        subscription_id=subscription_id
    )
    #获得负载均衡器1的信息
    #https://github.com/Azure-Samples/azure-samples-python-management/blob/main/doc/network-manage-loadbalancer/example_public_load_balancer.py#L198
    load_balancer = network_client.load_balancers.get(rg_name,loadbalacer_name)
    print("Get load balancer:\n{}".format(load_balancer))

    #获得负载均衡器2的信息
    load_balancer2 = network_client.load_balancers.get(rg_name,loadbalacer_name_2)

    
    # 根据虚拟机名称，获得网卡信息
    compute_client = ComputeManagementClient(credential = DefaultAzureCredential(),subscription_id = subscription_id)
    vm_name_1 = "NIO-EU-pv2-03"
    vm = compute_client.virtual_machines.get(rg_name,vm_name_1)
    
    vm_nic_id = vm.network_profile.network_interfaces[0].id
    vm_nic_name = vm_nic_id.split('networkInterfaces/')[1]

    #根据网卡名字，获得网卡属性
    network_interfaces = []
    network_interface = network_client.network_interfaces.get(rg_name,vm_nic_name)
    network_interfaces.append(network_interface)

    for i in range(1):
        for nic_ipconf in network_interfaces[i].ip_configurations:
            #如果这台虚拟机的网卡，需要加入到多个负载均衡器后端池，则可以在List里面执行多个后端池
            nic_ipconf.load_balancer_backend_address_pools = [load_balancer.backend_address_pools[0],load_balancer2.backend_address_pools[0]]

    #把网卡增加到负载均衡器后端       
    add_vm_to_lb_bp = network_client.network_interfaces.begin_create_or_update(
            rg_name,
            vm_nic_name,
            network_interfaces[0]
        ).result().ip_configurations
    
    print("Add {} to Load Balancer Backend Pool: \n{}".format(nic_ipconf.name, add_vm_to_lb_bp))
    
if __name__ == "__main__":
    main()