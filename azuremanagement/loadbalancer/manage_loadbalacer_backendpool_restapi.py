from asyncio import sleep
import os
import requests
import sys

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient


def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')
  
    # 1.先获得Access Token
    token_endpoint = f'https://login.microsoftonline.com/{tenantid}/oauth2/token'

    # Define the required parameters for the token endpoint
    data = {
        'grant_type': 'client_credentials',
        'client_id': clientid,
        'client_secret': clientsecret,
        'resource': 'https://management.azure.com/'
    }
    # Make a request to the token endpoint to obtain an access token
    response = requests.post(token_endpoint, data=data)
    # 获得Access Token
    access_token = response.json()['access_token']

    #2.再获得Load Balancer的资源ID
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    rg_name = "sig-rg"

    #NIO-EU-Hadoop-VMSS-2LB,后端池是网卡
    loadbalancer_name = "NIO-EU-Hadoop-VMSS-2LB"

    #NIO-EU-Hadoop-VMSS-2LB-IP01，后端池是内网IP
    #loadbalancer_name = "NIO-EU-Hadoop-VMSS-2LB-IP01"
    
    #后端池需要删除的IP地址
    remove_ip = "10.99.76.14"

    #后端池需要删除的虚拟机名称
    backendvm_name = "NIO-EU-pv2-03"

    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    network_client = NetworkManagementClient(credential = clientcredential,subscription_id = subscription_id)
    load_balancer = network_client.load_balancers.get(rg_name,loadbalancer_name)

    compute_client = ComputeManagementClient(credential = clientcredential,subscription_id = subscription_id)
    #找到这台虚拟机
    vm = compute_client.virtual_machines.get(rg_name,backendvm_name)
    #找到这台虚拟机的网卡信息
    vm_nic_id = vm.network_profile.network_interfaces[0].id
    
    #找到虚拟机网卡的ipConfigurations
    vm_nic_name = vm_nic_id.split('networkInterfaces/')[1]
    network_interface = network_client.network_interfaces.get(rg_name,vm_nic_name)

    get_nic_ipconfiguration_url = f"https://management.azure.com/{network_interface.ip_configurations[0].id}?api-version=2023-09-01"
    headers = {'Authorization': f'Bearer {access_token}'}

    get_nic_ipconfiguration_url_response = requests.get(get_nic_ipconfiguration_url,headers = headers)
    get_nic_ipconfiguration_url_data = get_nic_ipconfiguration_url_response.json()
    get_nic_ipconfiguration_id = get_nic_ipconfiguration_url_data['id']



    #3.拿到Load Balancer的所有属性
    get_url = f"https://management.azure.com/{load_balancer.id}?api-version=2022-09-01"
    headers = {'Authorization': f'Bearer {access_token}'}
    get_response = requests.get(get_url,headers = headers)

    get_json_data = get_response.json()

    #后端池，我们这里取第一个
    backend_pool_id = get_json_data['properties']['backendAddressPools'][0]['id']
    #后端池里的IP
    ips = get_json_data['properties']['backendAddressPools'][0]['properties']['loadBalancerBackendAddresses']

    #遍历Load Balancer后端的所有IP
    for ip in ips:
        #如果字典里存在ipAddress这个属性，则说明后端池是ip
        if 'ipAddress' in ip['properties']:
            if ip['properties']['ipAddress'] == remove_ip:
                lb_manage_backend_by_ip(access_token,backend_pool_id,remove_ip)

        #如果字典里存在networkInterfaceIPConfiguration，则说明后端池是网卡
        elif 'networkInterfaceIPConfiguration' in ip['properties']:
            # 如果在字典里，能找到虚拟机网卡的id信息,把这个虚拟机的网卡删除掉
            # backend_pool_id为后端池
            # vm_nic_id为后端池中，需要删除的虚拟机网卡ID
            if ip['properties']['networkInterfaceIPConfiguration']['id'] == get_nic_ipconfiguration_id:
                lb_manage_backend_by_nic(access_token,backend_pool_id,vm_nic_id)
        

def lb_manage_backend_by_ip(access_token,backend_pool_id,remove_ip):
    #https://learn.microsoft.com/en-us/rest/api/load-balancer/load-balancer-backend-address-pools/create-or-update?view=rest-load-balancer-2023-06-01
    
    get_lb_backend_addresspool_ip_url = f"https://management.azure.com/{backend_pool_id}?api-version=2023-06-01"
    headers = {'Authorization': f'Bearer {access_token}'}
    get_get_lb_backend_addresspool_ip_url_response = requests.get(get_lb_backend_addresspool_ip_url,headers = headers)
    get_lb_backend_addresspool_ip_data = get_get_lb_backend_addresspool_ip_url_response.json()

    #后端池里都是内网IP地址
    ips = get_lb_backend_addresspool_ip_data['properties']['loadBalancerBackendAddresses']

    #循环
    for ip in ips:
        if ip['properties']['ipAddress'] == remove_ip:
            ips.remove(ip)

    #重新提交REST API
    put_lb_backend_addresspool_ip_url = f"https://management.azure.com/{backend_pool_id}?api-version=2023-06-01"
    headers = {'Authorization': f'Bearer {access_token}'}
    put_response = requests.put(put_lb_backend_addresspool_ip_url,headers = headers,json = get_lb_backend_addresspool_ip_data)

    async_operation_url = put_response.headers['Azure-AsyncOperation']
    while check_async_status(access_token,async_operation_url) != 'Succeeded':
        print("没有执行成功")
        sleep(1)
    
    print("执行成功")


def lb_manage_backend_by_nic(access_token,backend_pool_id,nic_id):
    #https://learn.microsoft.com/en-us/rest/api/virtualnetwork/network-interfaces/get?view=rest-virtualnetwork-2023-09-01&tabs=HTTP


    '''
    https://management.azure.com/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/sig-rg/providers/Microsoft.Network/networkInterfaces/NIO-EU-pv2-01-nic/ipConfigurations/nic-ip-config?api-version=2023-09-01
    
    ################返回值################
    ######################################

    ################需要修改下面的loadBalancerBackendAddressPools
    ######################################

    {
        "name": "nic-ip-config",
        "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/sig-rg/providers/Microsoft.Network/networkInterfaces/NIO-EU-pv2-01-nic/ipConfigurations/nic-ip-config",
        "etag": "W/\"478bfec3-e53f-4e88-a511-778a080057aa\"",
        "type": "Microsoft.Network/networkInterfaces/ipConfigurations",
        "properties": {
            "provisioningState": "Succeeded",
            "privateIPAddress": "10.99.76.10",
            "privateIPAllocationMethod": "Dynamic",
            "subnet": {
                "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/sig-rg/providers/Microsoft.Network/virtualNetworks/NIO-EU/subnets/PROD-EU-AZURE-TOD-FE-VM-01"
            },
            "primary": true,
            "privateIPAddressVersion": "IPv4",
            "loadBalancerBackendAddressPools": [
                {
                    "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/sig-rg/providers/Microsoft.Network/loadBalancers/NIO-EU-Hadoop-VMSS-2LB/backendAddressPools/NIO-EU-Hadoop-VMSS-2LBBEPool"
                },
                {
                    "id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/sig-rg/providers/Microsoft.Network/loadBalancers/NIO-EU-Hadoop-VMSS-2LB-NIC/backendAddressPools/backendnic_pool"
                }
            ]
        }
    }
    '''

    get_nic_loadbalancerpool_url = f"https://management.azure.com/{nic_id}?api-version=2023-09-01"
    headers = {'Authorization': f'Bearer {access_token}'}

    get_nic_loadbalancerpool_url_response = requests.get(get_nic_loadbalancerpool_url,headers = headers)
    get_nic_loadbalancerpool_url_data = get_nic_loadbalancerpool_url_response.json()

    #网卡挂载到了loadBalancerBackendAddressPools
    ips = get_nic_loadbalancerpool_url_data['properties']['ipConfigurations'][0]['properties']['loadBalancerBackendAddressPools']

    #循环
    for ip in ips:
            if ip['id'] == backend_pool_id:
                ips.remove(ip)

    #重新提交REST API
    put_nic_ipconfiguration_url = f"https://management.azure.com/{nic_id}?api-version=2023-09-01"


    headers = {'Authorization': f'Bearer {access_token}'}
    put_response = requests.put(get_nic_loadbalancerpool_url,headers = headers,json = get_nic_loadbalancerpool_url_data)

    if put_response.status_code == 200:
        print("更新后端池的IP成功")






def check_async_status(access_token,async_operation_url):
    #https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/async-operations
    get_url = async_operation_url
    headers = {'Authorization': f'Bearer {access_token}'}

    get_response = requests.get(get_url,headers = headers)
    get_response_data = get_response.json()
    return get_response_data['status']


if __name__ == "__main__":
    main()