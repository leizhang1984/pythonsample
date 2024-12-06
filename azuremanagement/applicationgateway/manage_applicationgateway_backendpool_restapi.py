from asyncio import sleep
import os
import requests
import sys

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
'''
如果application gateway后端是ip地址，则需要对application gateway进行更新
如果application gateway后端是虚拟机网卡，则需要对虚拟机网卡属性进行更新操作
'''
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

    #2.再获得Application Gateway的资源ID
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    rg_name = "FW-Hybrid-Test"
    applicationgateway_name = "leiappgw02"
    
    # Create client
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    network_client = NetworkManagementClient(credential=clientcredential,subscription_id=subscription_id)
    application_gateway = network_client.application_gateways.get(rg_name,applicationgateway_name)


    #后端池需要删除的IP地址，如果后端池是ip，更新application gateway的属性
    remove_ip = "10.99.2.7"
    #后端池需要删除的虚拟机名称，如果后端池是虚拟机网卡，则更新虚拟机网卡的属性
    remove_vm_name = "nginxvm-03"
    #找到这台虚拟机
    compute_client = ComputeManagementClient(credential = clientcredential,subscription_id = subscription_id)
    vm = compute_client.virtual_machines.get(rg_name,remove_vm_name)
    
    #找到这台虚拟机的网卡信息，如果有多网卡，则遍历
    #这里只考虑，虚拟机只有一个网卡
    vm_nic_id = vm.network_profile.network_interfaces[0].id
    
    #找到虚拟机网卡的ipConfigurations
    vm_nic_name = vm_nic_id.split('networkInterfaces/')[1]
    network_interface = network_client.network_interfaces.get(rg_name,vm_nic_name)

    #找到虚拟机网卡的Ipconfig属性
    get_nic_ipconfiguration_url = f"https://management.azure.com/{network_interface.ip_configurations[0].id}?api-version=2023-09-01"
    headers = {'Authorization': f'Bearer {access_token}'}

    get_nic_ipconfiguration_url_response = requests.get(get_nic_ipconfiguration_url,headers = headers)
    get_nic_ipconfiguration_url_data = get_nic_ipconfiguration_url_response.json()
    get_nic_ipconfiguration_id = get_nic_ipconfiguration_url_data['id']
    
    #3.拿到Application Gateway的所有属性
    get_url = f"https://management.azure.com/{application_gateway.id}?api-version=2022-09-01"
    headers = {'Authorization': f'Bearer {access_token}'}
    get_response = requests.get(get_url,headers = headers)

    get_json_data = get_response.json()
    #4.如果后端池是IP地址，用下面的方法
    # ips = get_json_data['properties']['backendAddressPools'][0]['properties']['backendAddresses']

    # #遍历Application Gateway后端的所有IP
    # for ip in ips:
    #     #如果找到这个IP
    #     if ip['ipAddress'] == remove_ip:
    #         #把这个IP删除掉
    #         ips.remove(ip)
    
    # #5.把更新好的信息，重新提交
    # put_url = f"https://management.azure.com/{application_gateway.id}?api-version=2022-09-01"
    # headers = {'Authorization': f'Bearer {access_token}'}
    # put_response = requests.put(put_url,headers = headers,json=get_json_data)
        
    # print("执行成功")

    #6.如果后端池是虚拟机，用下面的方法
    backend_pool_id = get_json_data['properties']['backendAddressPools'][0]['id']
    nics = get_json_data['properties']['backendAddressPools'][0]['properties']['backendIPConfigurations']
   
    #遍历Application Gateway后端的所有网卡
    for nic in nics:
        #如果找到这个网卡
        if nic['id'] == get_nic_ipconfiguration_id:
            #把这个虚拟网卡上的信息，更新掉
            application_gateway_backend_by_nic(access_token,backend_pool_id,vm_nic_id)



def application_gateway_backend_by_nic(access_token,backend_pool_id,nic_id):
    get_nic_loadbalancerpool_url = f"https://management.azure.com/{nic_id}?api-version=2023-09-01"
    headers = {'Authorization': f'Bearer {access_token}'}

    get_nic_loadbalancerpool_url_response = requests.get(get_nic_loadbalancerpool_url,headers = headers)
    get_nic_loadbalancerpool_url_data = get_nic_loadbalancerpool_url_response.json()

    #网卡挂载到了loadBalancerBackendAddressPools
    ips = get_nic_loadbalancerpool_url_data['properties']['ipConfigurations'][0]['properties']['applicationGatewayBackendAddressPools']

    #循环
    for ip in ips:
            if ip['id'] == backend_pool_id:
                ips.remove(ip)

    #重新提交REST API
    put_nic_ipconfiguration_url = f"https://management.azure.com/{nic_id}?api-version=2023-09-01"


    headers = {'Authorization': f'Bearer {access_token}'}
    put_response = requests.put(get_nic_loadbalancerpool_url,headers = headers,json = get_nic_loadbalancerpool_url_data)

    if put_response.status_code == 200:
        print("更新后端池的网卡成功")
        

def check_async_status(access_token,async_operation_url):
    #https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/async-operations
    get_url = async_operation_url
    headers = {'Authorization': f'Bearer {access_token}'}

    get_response = requests.get(get_url,headers = headers)
    get_response_data = get_response.json()
    return get_response_data['status']


if __name__ == "__main__":
    main()