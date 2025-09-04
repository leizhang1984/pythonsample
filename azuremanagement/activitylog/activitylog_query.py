import sys,os
from datetime import datetime, timedelta, timezone
from azure.identity import ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resource import ResourceManagementClient


def main():
     # 替换为你的Service Principal信息
    tenant_id = os.environ.get('nonprod_tenantid')
    client_id = os.environ.get('nonprod_clientid')
    client_secret = os.environ.get('nonprod_clientsecret')

    credentials = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)
    #订阅名称
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    #资源组名称
    rg_name = "sig-rg"
    #资源名称
    resource_name = "Prometheus01"

    # 定义时间范围（例如过去2小时）
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=2)

    # 创建 ResourceManagementClient 实例
    resource_client = ResourceManagementClient(credentials, subscription_id)

    # 查找资源
    resource_list = resource_client.resources.list_by_resource_group(rg_name)
    resource_id = None
    for resource in resource_list:
        if resource.name == resource_name:
            resource_id = resource.id
            break
    
  
    if resource_id is None:
        print(f"Resource {resource_name} not found in resource group {rg_name}.")
        sys.exit(1)


    # 创建 MonitorManagementClient 实例
    monitor_client = MonitorManagementClient(credentials, subscription_id)
    
     # 创建 ResourceManagementClient 实例
    resource_client = ResourceManagementClient(credentials, subscription_id)
    # 构建查询过滤器
    filter_query = f"eventTimestamp ge '{start_time}' and eventTimestamp le '{end_time}' and resourceId eq '{resource_id}'"

    # 获取活动日志
    activity_logs = monitor_client.activity_logs.list(filter=filter_query)

    # 打印活动日志
    for log in activity_logs:
        print(f"Event Time: {log.event_timestamp}")
        print(f"Operation Name: {log.operation_name.localized_value}")
        print(f"Status: {log.status.localized_value}")
        print(f"Caller: {log.caller}")
        print(f"Description: {log.description}")
        print('-' * 60)

if __name__ == "__main__":
    main()
