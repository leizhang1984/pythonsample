import requests
import json
import os
import time
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

    # 获取用户指定的年月
    year = 2025
    month = 6

    # 获取用户指定月份的开始和结束日期
    first_day_of_specified_month = datetime(year, month, 1)
    first_day_of_next_month = first_day_of_specified_month + relativedelta(months=1)
    last_day_of_specified_month = first_day_of_next_month - timedelta(days=1)

    # 格式化日期为 ISO 8601 格式
    start_date = first_day_of_specified_month.strftime('%Y-%m-%dT00:00:00Z')
    end_date = last_day_of_specified_month.strftime('%Y-%m-%dT23:59:59Z')

    # 遍历所有订阅，生成费用详情报告
    for subscription in subscriptions:
        subscription_id = subscription['subscriptionId']
        subscription_name = subscription['displayName']
        
        # 构建请求 URL
        url  = f"https://management.azure.com/subscriptions/{subscription_id}/providers/Microsoft.CostManagement/generateCostDetailsReport?api-version=2023-11-01"

        # 构建请求体
        body={
            "metric": "ActualCost",
            "timePeriod": {
                "start": start_date,
                "end": end_date
            }
        }
 
        # 发送生成报告的请求
        response = requests.post(url, headers=headers, data=json.dumps(body))
        
        if response.status_code == 202:
            # 获取 Location 和 Retry-After 头信息
            location = response.headers['Location']
            retry_after = int(response.headers.get('Retry-After', 30))  # 默认等待 30 秒
            
            # 轮询直到报告生成完成
            while True:
                time.sleep(retry_after)
                poll_response = requests.get(location, headers=headers)
                
                if poll_response.status_code == 200:
                    # 报告生成完成，获取报告下载链接
                    report_data = poll_response.json()
                    blob_link = report_data['manifest']['blobs'][0]['blobLink']

                    print(f"Subscription Name: {subscription_name}")
                    print(f"Subscription ID: {subscription_id}")
                    print(f"Blob Link: {blob_link}")
                    # 后续需要把blob_link下载到本地，然后打开link里的文件进行处理
                    # 步骤略

                    break
                elif poll_response.status_code == 202:
                    # 继续轮询
                    retry_after = int(poll_response.headers.get('Retry-After', 30))
                else:
                    print(f"Failed to poll report for subscription: {subscription_name}")
                    print("Status Code:", poll_response.status_code)
                    print("Response:", poll_response.json())
                    break
        else:
            print(f"Failed to generate cost details report for subscription: {subscription_name}")
            print("Status Code:", response.status_code)
            print("Response:", response.json())

if __name__ == "__main__":
    main()
