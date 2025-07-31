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

def get_subscriptions(token):
    url = "https://management.azure.com/subscriptions?api-version=2020-01-01"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('value', [])
    else:
        print(f"Failed to retrieve subscriptions: {response.status_code}, {response.text}")
        response.raise_for_status()

def get_activity_logs(subscription_id, token, start_time, end_time):
    filter_condition = (
        f"eventTimestamp ge '{start_time.isoformat()}' and "
        f"eventTimestamp le '{end_time.isoformat()}' and "
        "operations eq 'Microsoft.Compute/virtualMachines/runCommand/action,Microsoft.Compute/virtualMachineScaleSets/virtualMachines/runCommand/action'"
    )
    url = f"https://management.azure.com/subscriptions/{subscription_id}/providers/microsoft.insights/eventtypes/management/values?api-version=2017-03-01-preview&$filter={filter_condition}"
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json().get('value', [])
    else:
        print(f"Failed to retrieve activity logs for subscription {subscription_id}: {response.status_code}, {response.text}")
        response.raise_for_status()

def main():
    tenant_id = os.environ.get('nonprod_tenantid')
    client_id = os.environ.get('nonprod_clientid')
    client_secret = os.environ.get('nonprod_clientsecret')

    # 获取访问令牌
    token = get_access_token(tenant_id, client_id, client_secret)

    # 获取所有订阅
    subscriptions = get_subscriptions(token)

    # 定义查询时间范围，例如过去 7 天
    end_time = datetime.now()
    start_time = end_time - timedelta(days=7)

    for subscription in subscriptions:
        subscription_id = subscription.get('subscriptionId')
        print(f"Processing subscription: {subscription_id}")
        
        # 获取活动日志
        activity_logs = get_activity_logs(subscription_id, token, start_time, end_time)
        
        # 处理查询结果
        for log in activity_logs:
            time_generated = log.get('eventTimestamp')
            caller = log.get('caller')
            clientipaddress = log.get('httpRequest', {}).get('clientIpAddress')
            resource_id = log.get('resourceId')
            operation_name = log.get('operationName', {}).get('value')
            status = log.get('status', {}).get('value')
            print(f"Time: {time_generated}, Caller: {caller}, Client IP: {clientipaddress},Resource: {resource_id}, Operation: {operation_name}, Status: {status}")

if __name__ == '__main__':
    main()
