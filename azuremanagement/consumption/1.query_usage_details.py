import requests
import json
import os
from datetime import datetime, timedelta
from azure.identity import ClientSecretCredential
from dateutil.relativedelta import relativedelta

def main():
    # 替换为你的 Azure AD 租户 ID、客户端 ID 和客户端密钥
    # 需要增加权限：Cost Management Reader
    tenant_id = os.environ.get('nonprod_tenantid')
    client_id = os.environ.get('nonprod_clientid')
    client_secret = os.environ.get('nonprod_clientsecret')

    # 获取访问令牌
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    access_token = credential.get_token('https://management.azure.com/.default').token

    # 设置请求头
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    # 获取所有订阅
    subscriptions_url = 'https://management.azure.com/subscriptions?api-version=2020-01-01'
    response = requests.get(subscriptions_url, headers=headers)
    subscriptions = response.json().get('value', [])

    # 获取用户指定的时间范围
    start_date_str = "2025-06-01"
    end_date_str = "2025-06-30"

    # 格式化日期为 ISO 8601 格式
    start_date = datetime.strptime(start_date_str, '%Y-%m-%d').strftime('%Y-%m-%dT00:00:00Z')
    end_date = datetime.strptime(end_date_str, '%Y-%m-%d').strftime('%Y-%m-%dT23:59:59Z')

    # 遍历所有订阅，获取费用详情
    for subscription in subscriptions:
        subscription_id = subscription['subscriptionId']
        subscription_name = subscription['displayName']
        
        # 构建请求 URL
        url = f'https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.Consumption/usageDetails?api-version=2021-10-01&$filter=date ge \'{start_date}\' and usageEnd le \'{end_date}\''

        # 发送请求
        response = requests.get(url, headers=headers)
        
        # 检查响应状态码
        if response.status_code == 200:
            data = response.json()
            usage_details = data.get('value', [])
            
            # 打印每个 usage_detail 的所有列和值
            print(f"Subscription: {subscription_name} ({subscription_id})")
            for detail in usage_details:
                print(json.dumps(detail, indent=4))
        else:
            print(f"Failed to retrieve usage details for subscription: {subscription_name}")
            print("Status Code:", response.status_code)
            print("Response:", response.json())

if __name__ == "__main__":
    main()
