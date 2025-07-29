import os
import requests
from datetime import datetime, timedelta

def get_access_token(tenant_id, client_id, client_secret):
    url = f"https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token"
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    body = {
        'grant_type': 'client_credentials',
        'client_id': client_id,
        'client_secret': client_secret,
        'scope': 'https://management.azure.com/.default'
    }
    response = requests.post(url, headers=headers, data=body)
    if response.status_code == 200:
        return response.json()['access_token']
    else:
        print(f"Failed to obtain access token: {response.status_code}, {response.text}")
        response.raise_for_status()

def main():
    tenant_id = os.environ.get('nonprod_tenantid')
    client_id = os.environ.get('nonprod_clientid')
    client_secret = os.environ.get('nonprod_clientsecret')

    # 设置订阅ID
    subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'

    # 获取访问令牌
    token = get_access_token(tenant_id, client_id, client_secret)

    # 定义查询时间范围，例如过去 7 天
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    # 定义过滤条件
    filter_condition = (
        f"eventTimestamp ge '{start_time.isoformat()}' and "
        f"eventTimestamp le '{end_time.isoformat()}' and "
        #"resourceProvider eq 'Microsoft.Compute'"
        " operations eq 'Microsoft.Compute/virtualMachines/runCommand/action'"
    )

    # 构建请求URL
    url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/microsoft.insights/eventtypes/management/values?api-version=2017-03-01-preview&$filter={filter_condition}"

    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }

    # 发送请求
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        activity_logs = response.json()
        # 处理查询结果
        for log in activity_logs.get('value', []):
            time_generated = log.get('eventTimestamp')
            caller = log.get('caller')
            resource_id = log.get('resourceId')
            operation_name = log.get('operationName', {}).get('value')
            status = log.get('status', {}).get('value')
            print(f"Time: {time_generated}, Caller: {caller}, Resource: {resource_id}, Operation: {operation_name}, Status: {status}")
    else:
        print(f"Failed to retrieve activity logs: {response.status_code}, {response.text}")
        response.raise_for_status()

if __name__ == '__main__':
    main()
