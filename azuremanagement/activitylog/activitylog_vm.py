import sys,os
from azure.identity import ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.compute import ComputeManagementClient
from datetime import datetime, timedelta, timezone



def main():
     # 替换为你的Service Principal信息
    tenant_id = os.environ.get('nonprod_tenantid')
    client_id = os.environ.get('nonprod_clientid')
    client_secret = os.environ.get('nonprod_clientsecret')

    credentials = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    rg_name = "sig-rg"
    #vm_name = "s-azeu3-mysqlmha-01"
    vm_name = "Prometheus01"
    # 创建 MonitorManagementClient 实例
    monitor_client = MonitorManagementClient(credentials, subscription_id)

   # 定义时间范围（例如过去2小时）
    end_time = datetime.now(timezone.utc)
    start_time = end_time - timedelta(hours=2)

    compute_client = ComputeManagementClient(credentials,subscription_id)
    # 构建查询过滤器
      # Get virtual machine
    vm = compute_client.virtual_machines.get(rg_name, vm_name)

    filter_query = f"eventTimestamp ge '{start_time}' and eventTimestamp le '{end_time}' and resourceId eq '{vm.id}'"

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
