import os
import time
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

    # 获取访问令牌
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)

    # 创建订阅客户端
    subscription_client = SubscriptionClient(credential)
    subscriptions = subscription_client.subscriptions.list()

    # 创建费用管理客户端
    cost_mgmt_client = CostManagementClient(credential)

    # 设置开始时间,为当前时间
    start_date = datetime.now()

    # 设置结束时间
    end_date = datetime(2099, 3, 31)

    # 格式化日期为 ISO 8601 格式
    start_date = start_date.strftime('%Y-%m-%dT00:00:00Z')
    end_date = end_date.strftime('%Y-%m-%dT23:59:59Z')

    # 创建Focus查询定义
    response = cost_mgmt_client.exports.create_or_update(
        #这里可以设置为订阅
        #也可以设置为管理组
        scope="/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6",
        export_name="monthly-amortized-sdk",
        parameters={
                "properties": {
                "schedule": {
                    "status": "Active",
                    # 设置为每月执行一次
                    "recurrence": "Monthly",
                    "recurrencePeriod": {
                        "from": start_date,
                        "to": end_date
                    }
                },

                "format": "Csv",
                "deliveryInfo": {
                "destination": {
                    "resourceId": "/subscriptions/166157a8-9ce9-400b-91c7-1d42482b83d6/resourceGroups/costmanagement-rg/providers/Microsoft.Storage/storageAccounts/leizhangcostmanagement01",
                    "container": "report",
                    "rootFolderPath": "monthly-amortized",
                    "type": "AzureBlob"
                }
                },
                "definition": {
                #设置类型为分摊成本
                "type": "amortizedCost",
                "timeframe": "MonthToDate",
                "dataSet": {
                    "configuration": {
                        "columns": [],
                        "dataVersion": "2021-10-01",
                        "filters": []
                    },
                    "granularity": "Daily",
                }
                },
                "partitionData": True,
                "dataOverwriteBehavior": "CreateNewReport",
                # 不压缩
                "compressionMode": "None",
                "exportDescription": ""
            }
        },
    )


    if(response.status_code == 200 or response.status_code == 201):
        print("Export created or updated successfully.")
    else:
        print(f"Failed to create or update export. Status code: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    main()

'''
https://github.com/nathanfalke/azure-sdk-for-python/blob/main/sdk/costmanagement/azure-mgmt-costmanagement/generated_samples/export_create_or_update_by_enrollment_account.py
'''