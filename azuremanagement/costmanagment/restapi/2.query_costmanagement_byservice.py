import requests
import json
import os
from datetime import datetime, timedelta
from azure.identity import ClientSecretCredential

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

    # 初始化结果字典
    cost_by_subscription = {}

    # 获取用户指定的年月
    year = int(2025)
    month = int(6)

    # 获取用户指定月份的开始和结束日期
    first_day_of_specified_month = datetime(year, month, 1)
    if month == 12:
        first_day_of_next_month = datetime(year + 1, 1, 1)
    else:
        first_day_of_next_month = datetime(year, month + 1, 1)
    last_day_of_specified_month = first_day_of_next_month - timedelta(days=1)

    # 格式化日期为 ISO 8601 格式
    start_date = first_day_of_specified_month.strftime('%Y-%m-%dT%H:%M:%SZ')
    end_date = last_day_of_specified_month.strftime('%Y-%m-%dT%H:%M:%SZ')

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
                },
                "grouping": [
                    {
                        "type": "Dimension",
                        "name": "meterCategory"
                    }
                ]
            }
        }
        
        # 发送请求
        response = requests.post(url, headers=headers, data=json.dumps(body))
        
        # 检查响应状态码
        if response.status_code == 200:
            data = response.json()
            columns = data['properties']['columns'] if 'properties' in data and 'columns' in data['properties'] else []
            rows = data['properties']['rows'] if 'properties' in data and 'rows' in data['properties'] else []
            
            # 提取列名
            column_names = [col['name'] for col in columns]
            
            # 初始化服务类型费用字典
            service_costs = []
            for row in rows:
                row_data = {column_names[i]: row[i] for i in range(len(row))}
                service_costs.append(row_data)
            
            cost_by_subscription[subscription_name] = service_costs
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
{
    "leizhang-non-prod": [
        {
            "Cost": 0.793032761290323,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Azure DNS",
            "Currency": "USD"
        },
        {
            "Cost": 0.0,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Azure Data Explorer",
            "Currency": "USD"
        },
        {
            "Cost": 0.00024,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Azure Data Factory v2",
            "Currency": "USD"
        },
        {
            "Cost": 32.7552586,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Azure Database for MySQL",
            "Currency": "USD"
        },
        {
            "Cost": 900.0,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Azure Firewall",
            "Currency": "USD"
        },
        {
            "Cost": 4e-05,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Azure Monitor",
            "Currency": "USD"
        },
        {
            "Cost": 0.579534696517527,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Bandwidth",
            "Currency": "USD"
        },
        {
            "Cost": 3.46706,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Cognitive Services",
            "Currency": "USD"
        },
        {
            "Cost": 39.996319968,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Container Registry",
            "Currency": "USD"
        },
        {
            "Cost": 0.005817,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Event Grid",
            "Currency": "USD"
        },
        {
            "Cost": 45.645166796,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Event Hubs",
            "Currency": "USD"
        },
        {
            "Cost": 0.0,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Insight and Analytics",
            "Currency": "USD"
        },
        {
            "Cost": 0.00081,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Key Vault",
            "Currency": "USD"
        },
        {
            "Cost": 126.397281385394,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Load Balancer",
            "Currency": "USD"
        },
        {
            "Cost": 0.00126762246,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Log Analytics",
            "Currency": "USD"
        },
        {
            "Cost": 1.20456508092871,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Logic Apps",
            "Currency": "USD"
        },
        {
            "Cost": 284.399628113055,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Microsoft Defender for Cloud",
            "Currency": "USD"
        },
        {
            "Cost": 0.001121,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Service Bus",
            "Currency": "USD"
        },
        {
            "Cost": 1008.2235616943,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Storage",
            "Currency": "USD"
        },
        {
            "Cost": 0.0,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Virtual Machine Licenses",
            "Currency": "USD"
        },
        {
            "Cost": 404.407420192,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Virtual Machines",
            "Currency": "USD"
        },
        {
            "Cost": 344.099552777778,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Virtual Network",
            "Currency": "USD"
        },
        {
            "Cost": 180.0,
            "BillingMonth": "2025-06-01T00:00:00",
            "meterCategory": "Virtual WAN",
            "Currency": "USD"
        }
    ]
}
'''