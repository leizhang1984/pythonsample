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

    # 初始化结果列表
    cost_by_subscription = []

    # 获取用户指定的年月
    year = int(2025)
    month = int(6)

    # 获取用户指定月份的开始和结束日期
    first_day_of_specified_month = datetime(year, month, 1)
    first_day_of_next_month = first_day_of_specified_month + relativedelta(months=1)
    last_day_of_specified_month = first_day_of_next_month - timedelta(days=1)

    # 格式化日期为 ISO 8601 格式
    start_date = first_day_of_specified_month.strftime('%Y-%m-%dT00:00:00Z')
    end_date = last_day_of_specified_month.strftime('%Y-%m-%dT23:59:59Z')

    # 遍历所有订阅，获取费用详情
    for subscription in subscriptions:
        subscription_id = subscription['subscriptionId']
        subscription_name = subscription['displayName']
        
        # 构建请求 URL
        url = f'https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/query?api-version=2025-03-01'
        
        # 构建请求体
        body = {
            "type": "Usage",
            "timeframe": "Custom",
            "timePeriod": {
                "from": start_date,
                "to": end_date
            },
            "dataset": {
                "granularity": "Monthly",
                "aggregation": {
                    "totalCost": {
                        "name": "Cost",
                        "function": "Sum"
                    }
                }
            }
        }
        
        # 发送请求
        response = requests.post(url, headers=headers, data=json.dumps(body))
        
        # 检查响应状态码
        if response.status_code == 200:
            data = response.json()
            total_cost = data['properties']['rows'][0][0] if data['properties']['rows'] else 0
            cost_by_subscription.append({
                'subscriptionName': subscription_name,
                'subscriptionId': subscription_id,
                'totalCost': total_cost
            })
        else:
            print(f"Failed to retrieve cost data for subscription: {subscription_name}")
            print("Status Code:", response.status_code)
            print("Response:", response.json())

    # 输出结果
    print(json.dumps(cost_by_subscription, indent=4))

if __name__ == "__main__":
    main()

'''
返回结果
[
    {
        "subscriptionName": "leizhang-non-prod",
        "subscriptionId": "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx",
        "totalCost": 3371.97767768772
    }
]
'''
