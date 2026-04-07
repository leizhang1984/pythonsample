import requests
import json
import os
from datetime import datetime, timedelta
from azure.identity import ClientSecretCredential
from dateutil.relativedelta import relativedelta

def main():
    # 替换为你的 Azure AD 租户 ID、客户端 ID 和客户端密钥
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
        # type支持三种类型：
        # 1.Usage，表示用量
        # 2.ActualCost，表示实际费用
        # 3.AmortizedCost，表示分摊费用
        body = {
            'type': 'AmortizedCost',
            'dataSet': {
                'granularity': 'Monthly',
                'aggregation': {
                    'totalCost': {
                        'name': 'Cost',
                        'function': 'Sum'
                    }
                },
                'grouping': [
                    {'type': 'Dimension', 'name': 'ResourceId'},
                    {'type': 'Dimension', 'name': 'ServiceName'},
                    {'type': 'Dimension', 'name': 'SubscriptionName'}
                ]
            },
            'timeframe': 'Custom',
            'timePeriod': {
                "from": start_date,
                "to": end_date
            }
        }

        # 发送请求并处理分页
        all_data = []

        while url:
            response = requests.post(url, headers=headers, data=json.dumps(body))
            
            # 检查响应状态码
            if response.status_code == 200:
                data = response.json()
                all_data.extend(data.get('properties', {}).get('rows', []))
                
                # 检查是否有下一页
                url = data.get('properties', {}).get('nextLink', None)
            else:
                print(f"Failed to retrieve cost data. Status Code: {response.status_code}")
                print("Response:", response.json())
                break
        
        # 将结果写入 JSON 文件
        with open(f'query_subscription_amortized_paging_{subscription_name}.json', 'w') as json_file:
            json.dump(all_data, json_file, indent=4)
            print(f"Results have been written to query_subscription_amortized_paging_{subscription_name}.json")


   

if __name__ == "__main__":
    main()
