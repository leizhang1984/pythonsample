import json
import os,time,requests
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.costmanagement import CostManagementClient

def main():
    # 替换为你的 Azure AD 租户 ID、客户端 ID 和客户端密钥
    # 需要设置Service Principal的权限为Cost Management Contributor
    tenant_id = os.environ.get('nonprod_tenantid')
    client_id = os.environ.get('nonprod_clientid')
    client_secret = os.environ.get('nonprod_clientsecret')


    # 设置开始时间
    start_date = datetime(2026, 3, 1)

    # 设置结束时间
    end_date = datetime(2026, 3, 31)

    # 格式化日期为 ISO 8601 格式
    start_date = start_date.strftime('%Y-%m-%dT00:00:00Z')
    end_date = end_date.strftime('%Y-%m-%dT23:59:59Z')

    # 获取访问令牌
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)
    access_token = credential.get_token('https://management.azure.com/.default').token

    # 设置请求头
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }

    subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'
    scope = f'subscriptions/{subscription_id}'

    export_name = 'daily-focus-restapi'
     # 构建请求 URL
    url = f'https://management.azure.com/{scope}/providers/Microsoft.CostManagement/exports/{export_name}?api-version=2025-03-01'

     # 3.AmortizedCost，表示分摊费用
    body = {
        "properties": {
        "schedule": {
                "status": "Active",
                "recurrence": "Daily",
                "recurrencePeriod": {
                    "from": "2025-08-06T00:00:00Z",
                    "to": "2050-02-01T00:00:00Z"
                }
                },
            "definition": {
                "type": "FocusCost",
                "timeframe": "MonthToDate",
                "dataSet": {
                    "configuration": {
                    "columns": [],
                    "dataVersion": "1.0r2",
                    "filters": []
                    },
                    "granularity": "Daily"
                    }
                },
            "deliveryInfo": {
            "destination": {
                "container": "report",
                "rootFolderPath": "daily-focus",
                "resourceId": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/costmanagement-rg/providers/Microsoft.Storage/storageAccounts/leizhangcostmanagement01",
            }
            },
            "format": "Csv",
            "partitionData": True,
            #不压缩
            "compressionMode": "None",
            "dataOverwriteBehavior": "CreateNewReport",
        }
    }


    response = requests.put(url, headers=headers, data=json.dumps(body))
    if(response.status_code == 200 or response.status_code == 201):
        print("Export created or updated successfully.")
    else:
        print(f"Failed to create or update export. Status code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    main()
