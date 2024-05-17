from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient

# 用您的Azure订阅ID替换此处
subscription_id = '8562f68b-3b70-4aa7-9ea0-f033a7ec676e'
# 用您的资源组名称和虚拟网络名称替换此处
resource_group_name = 'mc_aks-ppg-test_ppgakscluster_eastus'
vm_name = 'your_virtual_machine_name'

# 使用默认凭据（如 CLI 登录的用户、环境变量、MSI 等）设置 Azure 认证
credential = DefaultAzureCredential()

# 创建一个网络管理客户端实例
network_client = NetworkManagementClient(credential, subscription_id)

# 用您的专线路由表名称替换此处
route_table_name = 'aks-agentpool-18492298-routetable'

# 获取专线路由表信息
route_table = network_client.route_tables.get(resource_group_name, route_table_name)

# 遍历专线路由表中的路由规则并打印具体条目信息
for route in route_table.routes:
    print(f"Route Name: {route.name}, Address Prefix: {route.address_prefix}, Next Hop Type: {route.next_hop_type}, Next Hop IP: {route.next_hop_ip_address}")