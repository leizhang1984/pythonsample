import os

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import *

def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    rg_name = "sig-rg"
    loadbalacer_name = "NIO-EU-Hadoop-VMSS-2LB"
    location = "germanywestcentral"

    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    network_client = NetworkManagementClient(
        credential=clientcredential,
        subscription_id=subscription_id
    )
    #获得负载均衡器信息
    load_balancer = network_client.load_balancers.get(rg_name,loadbalacer_name)
    print("Get load balancer:\n{}".format(load_balancer))
    
    #Get Probe
    probes = load_balancer.probes
    for probe in probes:
        print(probe)

    #获得负载均衡器的后端池名称
    #lb_backend_address_pools_name =load_balancer.backend_address_pools[0].name
    #print("Get load balancer Backend Pool:\n{}".format(lb_backend_address_pools_name))

    #Get backend pool by name 01 (NIC Name)
    backend_pool_01 = network_client.load_balancer_backend_address_pools.get(rg_name,loadbalacer_name,"NIO-EU-Hadoop-VMSS-2LBBEPool")

    lb_backend_addresses_01 = backend_pool_01.load_balancer_backend_addresses
    #List back end pool NIC Id
    for lb_backend_addr in lb_backend_addresses_01:
        print(lb_backend_addr.network_interface_ip_configuration.id)
    

    #Create Resource Graph Client
    resourcegraph_client = ResourceGraphClient(
        credential = clientcredential,
        subscription_id = subscription_id
    )

    #Get Backend pool by Name 02 (Private IP Address)
    backend_pool_02 = network_client.load_balancer_backend_address_pools.get(rg_name,loadbalacer_name,"Pool02")
    lb_backend_addresses_02 = backend_pool_02.load_balancer_backend_addresses
    #List back end pool NIC Id
    for lb_backend_addr in lb_backend_addresses_02:
        vm_private_ip = lb_backend_addr.ip_address

        #Get VM Name by Private IP Address
        query = QueryRequest(
            query=f'''Resources
                | where type =~ 'microsoft.compute/virtualmachines'
                | project vmId = tolower(tostring(id)), vmName = name
                | join (Resources
                    | where type =~ 'microsoft.network/networkinterfaces'
                    | mv-expand ipconfig=properties.ipConfigurations
                    | project vmId = tolower(tostring(properties.virtualMachine.id)), privateIp = ipconfig.properties.privateIPAddress, publicIpId = tostring(ipconfig.properties.publicIPAddress.id)
                    | join kind=leftouter (Resources
                        | where type =~ 'microsoft.network/publicipaddresses'
                        | project publicIpId = id, publicIp = properties.ipAddress
                    ) on publicIpId
                    | project-away publicIpId, publicIpId1
                    | summarize privateIps = make_list(privateIp), publicIps = make_list(publicIp) by vmId
                ) on vmId
                | project-away vmId1
                | sort by vmName asc | where privateIps contains "{vm_private_ip}" ''',
            subscriptions=[subscription_id]
        )

        query_response = resourcegraph_client.resources(query)

        queryresult_vm_name = query_response.data[0]['vmName']
        queryresult_vm_privateip = query_response.data[0]['privateIps']
       
        print("Basic query vm name is: {}".format(queryresult_vm_name))
        print("Basic query vm private ip is: {}".format(queryresult_vm_privateip))


if __name__ == "__main__":
    main()