import os
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resourcehealth import ResourceHealthMgmtClient
#pip3  install  azure-mgmt-resourcehealth

def get_vm_resource_health(subscription_id, tenant_id, client_id, client_secret, resource_group_name, vm_name):
    # 使用ClientSecretCredential进行身份验证
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)

    # 创建计算管理客户端
    compute_client = ComputeManagementClient(credential, subscription_id)

    # 获取虚拟机的详细信息
    try:
        vm = compute_client.virtual_machines.get(resource_group_name, vm_name)
        resource_id = vm.id
        print(f"Resource ID: {resource_id}")
    except Exception as e:
        print(f"Error retrieving VM details for '{vm_name}': {e}")
        return

    # 创建Resource Health管理客户端
    resource_health_client = ResourceHealthMgmtClient(credential, subscription_id)

    try:

        response = resource_health_client.events.list_by_single_resource(resource_id)
        for item in response:
            print(f"Time is {item.impact_start_time}, Reason is {item.reason}, Title is {item.title}, summary is {item.summary}")

    except Exception as e:
        print(f"Error retrieving resource health for VM '{vm_name}': {e}")

def main():
     # 替换为你的Service Principal信息
    tenant_id = os.environ.get('nonprod_tenantid')
    client_id = os.environ.get('nonprod_clientid')
    client_secret = os.environ.get('nonprod_clientsecret')

    subscription_id = 'ffe7c7cd-f495-444a-9df7-9bcb39da2d66'
    
    # 指定的资源组名称和虚拟机名称
    resource_group_name = 'RG-TEST'
    vm_name = 'canary-vm'

    get_vm_resource_health(subscription_id, tenant_id, client_id, client_secret, resource_group_name, vm_name)


if __name__ == "__main__":
    main()
