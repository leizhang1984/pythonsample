import os
from azure.identity import ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from datetime import datetime, timedelta



def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    #设置订阅ID
    subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'
    
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    monitorclient = MonitorManagementClient(clientcredential, subscription_id)

    # 定义查询时间范围，例如过去 7 天
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    # 定义过滤条件，使用换行符提高可读性
    # 用python sdk只能filter: resourceProvider。不能filter其他内容
    filter_condition = (
        f"eventTimestamp ge '{start_time.isoformat()}' and "
        f"eventTimestamp le '{end_time.isoformat()}' and "
        "resourceProvider eq 'Microsoft.Compute' and "
        #"operations eq 'Microsoft.Compute/virtualMachines/runCommand/action'"
    )

    # 查询活动日志
    activity_logs = monitorclient.activity_logs.list(
        filter=filter_condition
    )

    # 处理查询结果
    for log in activity_logs:
        if log.operation_name.value == "Microsoft.Compute/virtualMachines/runCommand/action":
            time_generated = log.event_timestamp
            caller = log.caller
            resource_id = log.resource_id
            operation_name = log.operation_name.value
            status = log.status.value
            print(f"Time: {time_generated}, Caller: {caller}, Resource: {resource_id}, Operation: {operation_name}, Status: {status}")



if __name__ == '__main__':
    main()
