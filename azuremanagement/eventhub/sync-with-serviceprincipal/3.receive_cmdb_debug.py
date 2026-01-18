import os
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.identity import ClientSecretCredential

# 资源列表

#可以通过Azure Resource Graph查询得到类似的数据，然后放到这里进行调试
# resourcechanges
# | extend changeTime=todatetime(properties.changeAttributes.timestamp)
# | order by changeTime desc
# | extend operatioName= properties.changeAttributes.operation
# | extend resourceid = properties.targetResourceId
# | limit 100


resources = [
    [
        {
            "subscription_id": "166157a8-9ce9-400b-91c7-1d42482b83d6",
            "operation_name": "Microsoft.Compute/virtualMachines/write",
            "resource_id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/lun-rg/providers/Microsoft.Compute/virtualMachines/centos-lun"
        },
        {
            "subscription_id": "166157a8-9ce9-400b-91c7-1d42482b83d6",
            "operation_name": "Microsoft.Storage/storageAccounts/write",
            "resource_id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/lab-rg/providers/Microsoft.Storage/storageAccounts/azuremonitorns01"
        }
    ],
    [
        {
            "subscription_id": "166157a8-9ce9-400b-91c7-1d42482b83d6",
            "operation_name": "Microsoft.Network/virtualNetworks/subnets/write",
            "resource_id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/vwan-rg/providers/Microsoft.Network/virtualNetworks/westus3-prod-vnet01/subnets/default"
        }
    ],
    [
        {
            "subscription_id": "166157a8-9ce9-400b-91c7-1d42482b83d6",
            "operation_name": "Microsoft.Network/virtualNetworks/write",
            "resource_id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/vwan-rg/providers/Microsoft.Network/virtualNetworks/westus3-prod-vnet01"
        }
    ],
    [
        {
            "subscription_id": "166157a8-9ce9-400b-91c7-1d42482b83d6",
            "operation_name": "Microsoft.Compute/disks/write",
            "resource_id": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourcegroups/fw-hybrid-test/providers/Microsoft.Compute/disks/myNewDataDisk"
        }
    ]
]

# 使用服务主体进行身份验证
tenant_id = os.environ.get('nonprod_tenantid')
client_id = os.environ.get('nonprod_clientid')
client_secret = os.environ.get('nonprod_clientsecret')

sync_credential = ClientSecretCredential(tenant_id, client_id, client_secret)

# 获取资源信息
def get_resource(credential, subscription_id, operation_name, resource_id):

    # 下面的API Version不能随意更改，需要根据具体资源类型选择合适的版本
    # 下面的get_by_id没办法继续使用
    '''
    Exception has occurred: HttpResponseError
    (NoRegisteredProviderFound) No registered resource provider found for location 'japaneast' and API version '2024-01-01' for type 'virtualMachines'. 
    The supported api-versions are '2015-05-01-preview, 2015-06-15, 2016-03-30, 2016-04-30-preview, 2016-08-30, 2017-03-30, 2017-12-01, 2018-04-01, 2018-06-01, 2018-10-01, 2019-03-01, 2019-07-01, 2019-12-01, 2020-06-01, 2020-12-01, 2021-03-01, 2021-04-01, 2021-07-01, 2021-11-01, 2022-03-01, 2022-08-01, 2022-11-01, 2023-03-01, 2023-07-01, 2023-09-01, 2024-03-01, 2024-07-01, 2024-11-01, 2025-04-01'. The supported locations are 'eastus, eastus2, westus, centralus, northcentralus, southcentralus, northeurope, westeurope, eastasia, southeastasia, japaneast, japanwest, australiaeast, australiasoutheast, australiacentral, brazilsouth, southindia, centralindia, westindia, canadacentral, canadaeast, westus2, westcentralus, uksouth, ukwest, koreacentral, koreasouth, francecentral, southafricanorth, uaenorth, switzerlandnorth, germanywestcentral, norwayeast, jioindiawest, westus3, swedencentral, qatarcen
    
    
    Exception has occurred: HttpResponseError
    (NoRegisteredProviderFound) No registered resource provider found for location 'japaneast' and API version '2025-04-01' for type 'storageAccounts'. 
    The supported api-versions are '2025-06-01, 2025-01-01, 2024-01-01, 2023-05-01, 2023-04-01, 2023-01-01, 2022-09-01, 2022-05-01, 2021-09-01, 2021-08-01, 2021-06-01, 2021-05-01, 2021-04-01, 2021-02-01, 2021-01-01, 2020-08-01-preview, 2019-06-01, 2019-04-01, 2018-11-01, 2018-07-01, 2018-03-01-preview, 2018-02-01, 2017-10-01, 2017-06-01, 2016-12-01, 2016-05-01, 2016-01-01, 2015-06-15, 2015-05-01-preview'. The supported locations are 'eastus, eastus2, westus, westeurope, eastasia, southeastasia, japaneast, japanwest, northcentralus, southcentralus, centralus, northeurope, brazilsouth, australiaeast, australiasoutheast, southindia, centralindia, westindia, canadaeast, canadacentral, westus2, westcentralus, uksouth, ukwest, koreacentral, koreasouth, francecentral, australiacentral, southafricanorth, uaenorth, switzerlandnorth, germanywestcentral, norwayeast, westus3, jioindiawest, swedencentral, qatarcentral, polandcentral, italynorth, israelcentral, mexicocentral, spaincentral, newzealandnorth, indonesiacentral, malaysiawest, chilecentral, austriaeast, belgiumcentral'.
    '''


    # resource_management_client = ResourceManagementClient(credential, subscription_id)
    # api_version = "2025-04-01"  
    # resource = resource_management_client.resources.get_by_id(resource_uri, api_version)


    if "Microsoft.Compute/virtualMachines" in operation_name:
        get_vm(credential, subscription_id, resource_id)
    elif "Microsoft.Storage/storageAccounts" in operation_name:
        get_storage(credential, subscription_id, resource_id)
    elif "subnets" in operation_name:
        get_vnet_and_subnet(credential, subscription_id, resource_id)
    elif "Microsoft.Network/virtualNetworks" in operation_name:
        get_vnet(credential, subscription_id, resource_id)
    elif "Microsoft.Network/networkSecurityGroups" in operation_name:
        get_nsg(credential, subscription_id, resource_id)
    elif "Microsoft.Compute/disks" in operation_name:
        get_disk(credential, subscription_id, resource_id)
    # 你可以根据需要添加更多的条件判断

# 处理虚拟机资源
def get_vm(credential, subscription_id, resource_id):
    print("******************************************************")
    print("******************************************************")
    print("Get the Virtual Machine")
 
    resource_parts = resource_id.split('/')
    resource_group = resource_parts[4]
    vm_name = resource_parts[8]

    compute_client = ComputeManagementClient(credential, subscription_id)
    vm = compute_client.virtual_machines.get(resource_group, vm_name)
    print(f"VM Name: {vm.name}")
    print(f"VM Location: {vm.location}")
    print(f"VM Size: {vm.hardware_profile.vm_size}")
    print(f"VM Availability Zone: {vm.zones}")

    vm_instance_view = compute_client.virtual_machines.instance_view(resource_group, vm_name)
    # 虚拟机运行状态
    print(f"VM Status: {vm_instance_view.statuses[1].display_status}")

# 处理存储账户资源
def get_storage(credential, subscription_id, resource_id):
    print("******************************************************")
    print("******************************************************")
    print("Get the Storage Account")

    resource_parts = resource_id.split('/')
    resource_group = resource_parts[4]
    storageaccount_name = resource_parts[8]

    storage_client = StorageManagementClient(credential, subscription_id)
    storage_account = storage_client.storage_accounts.get_properties(resource_group, storageaccount_name)
    # 存储账户的状态
    print(f"Storage Account Name: {storage_account.name}")
    print(f"Storage Account Status: {storage_account.provisioning_state}")
    print(f"Storage Account Access Tier: {storage_account.access_tier}")
    print(f"Storage Account Location: {storage_account.location}")
    print(f"Storage Account Public Network Access: {storage_account.public_network_access}")

#处理虚拟机磁盘
def get_disk(credential, subscription_id, resource_id):
    print("******************************************************")
    print("******************************************************")
    print("Get the Disk")

    resource_parts = resource_id.split('/')
    resource_group = resource_parts[4]
    disk_name = resource_parts[8]

    compute_client = ComputeManagementClient(credential, subscription_id)
    disk = compute_client.disks.get(resource_group, disk_name)
    print(f"Disk Name: {disk.name}")
    print(f"Disk Location: {disk.location}")
    print(f"Disk Size (GB): {disk.disk_size_gb}")
    print(f"Disk SKU: {disk.sku.name}")
    print(f"Disk IOPS: {disk.disk_iops_read_write}")
    print(f"Disk Throughput: {disk.disk_m_bps_read_write}")
    print(f"Disk State: {disk.disk_state}")
    print(f"Disk Provisioning State: {disk.provisioning_state}")


# 处理虚拟网络资源
def get_vnet(credential, subscription_id, resource_id):
    print("******************************************************")
    print("******************************************************")
    print("Get the Virtual Network and Subnet")

    resource_parts = resource_id.split('/')
    resource_group = resource_parts[4]
    vnet_name = resource_parts[8]

    network_client = NetworkManagementClient(credential, subscription_id)
    vnet = network_client.virtual_networks.get(resource_group, vnet_name)
    print(f"VNet Name: {vnet.name}")
    print(f"VNet Location: {vnet.location}")
    # 遍历并打印VNet的所有地址空间
    print("VNet Address Spaces:")
    for address_prefix in vnet.address_space.address_prefixes:
        print(f" - {address_prefix}")


    # 打印VNet的DNS服务器信息
    if vnet.dhcp_options and vnet.dhcp_options.dns_servers:
        print("VNet DNS Servers:")
        for dns_server in vnet.dhcp_options.dns_servers:
            print(f" - {dns_server}")

# 处理虚拟网络和子网资源
def get_vnet_and_subnet(credential, subscription_id, resource_id):
    print("******************************************************")
    print("******************************************************")
    print("Get the Virtual Network and Subnet")

    resource_parts = resource_id.split('/')
    resource_group = resource_parts[4]
    vnet_name = resource_parts[8]
    subnet_name = resource_parts[10]

    network_client = NetworkManagementClient(credential, subscription_id)
    vnet = network_client.virtual_networks.get(resource_group, vnet_name)
    print(f"VNet Name: {vnet.name}")
    print(f"VNet Location: {vnet.location}")
    # 遍历并打印VNet的所有地址空间
    print("VNet Address Spaces:")
    for address_prefix in vnet.address_space.address_prefixes:
        print(f" - {address_prefix}")

    # 打印VNet的DNS服务器信息
    if vnet.dhcp_options and vnet.dhcp_options.dns_servers:
        print("VNet DNS Servers:")
        for dns_server in vnet.dhcp_options.dns_servers:
            print(f" - {dns_server}")


   # 获取并遍历VNet的所有子网
    print("Subnets:")
    subnets = network_client.subnets.list(resource_group, vnet_name)
    for subnet in subnets:
        print(f"Subnet Name: {subnet.name}")
        print(f" - Address Prefix: {subnet.address_prefix}")


# 处理NSG
def get_nsg(credential, subscription_id, resource_id):
    print("******************************************************")
    print("******************************************************")
    print("Get the Network Security Group")

    resource_parts = resource_id.split('/')
    resource_group = resource_parts[4]
    nsg_name = resource_parts[8]

    network_client = NetworkManagementClient(credential, subscription_id)
    nsg = network_client.network_security_groups.get(resource_group, nsg_name)

    # 网络安全组的状态
    print(f"NSG Name: {nsg.name}")
    print(f"NSG Location: {nsg.location}")
    print(f"NSG Security Rules: {len(nsg.security_rules)}")

    # 遍历入站规则
    print("\nInbound Security Rules:")
    for rule in nsg.security_rules:
        if rule.direction == "Inbound":
            print(f" - Name: {rule.name}")
            print(f"   Priority: {rule.priority}")
            print(f"   Access: {rule.access}")
            print(f"   Protocol: {rule.protocol}")
            print(f"   Source Port Range: {rule.source_port_range}")
            print(f"   Destination Port Range: {rule.destination_port_range}")
            print(f"   Source Address Prefix: {rule.source_address_prefix}")
            print(f"   Destination Address Prefix: {rule.destination_address_prefix}")
            print(f"   Description: {rule.description}")

    # 遍历出站规则
    print("\nOutbound Security Rules:")
    for rule in nsg.security_rules:
        if rule.direction == "Outbound":
            print(f" - Name: {rule.name}")
            print(f"   Priority: {rule.priority}")
            print(f"   Access: {rule.access}")
            print(f"   Protocol: {rule.protocol}")
            print(f"   Source Port Range: {rule.source_port_range}")
            print(f"   Destination Port Range: {rule.destination_port_range}")
            print(f"   Source Address Prefix: {rule.source_address_prefix}")
            print(f"   Destination Address Prefix: {rule.destination_address_prefix}")
            print(f"   Description: {rule.description}")





# 主程序
def main():
    credential = sync_credential  # 使用服务主体进行身份验证
    for items in resources:
        for item in items:
            subscription_id = item["subscription_id"]
            operation_name = item["operation_name"]
            resource_id = item["resource_id"]
            get_resource(credential, subscription_id, operation_name, resource_id)

if __name__ == "__main__":
    main()
