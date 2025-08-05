import os
import time
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
from azure.identity import ClientSecretCredential
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.costmanagement import CostManagementClient
from azure.mgmt.costmanagement.models import QueryDefinition,ExportType,CostDetailsOperationResults,GenerateCostDetailsReportRequestDefinition,CostDetailsMetricType,CostDetailsTimePeriod

def main():
    # 替换为你的 Azure AD 租户 ID、客户端 ID 和客户端密钥
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

    # 设置开始时间为2025年6月1日
    start_date = datetime(2025, 6, 1)

    # 设置结束时间为2025年7月31日
    end_date = datetime(2025, 7, 31)

    # 格式化日期为 ISO 8601 格式
    start_date = start_date.strftime('%Y-%m-%dT00:00:00Z')
    end_date = end_date.strftime('%Y-%m-%dT23:59:59Z')

    # 遍历所有订阅，生成费用详情报告
    for subscription in subscriptions:
        subscription_id = subscription.subscription_id
        subscription_name = subscription.display_name


        # Query
        response = cost_mgmt_client.query.usage(
            scope = f"subscriptions/{subscription_id}",  
            parameters={
                "dataset": {
                    # "filter": {
                    #     "and": [
                    #         {
                    #             "or": [
                    #                 {
                    #                     "dimensions": {
                    #                         "name": "ResourceLocation",
                    #                         "operator": "In",
                    #                         "values": ["East US", "West Europe"],
                    #                     }
                    #                 },
                    #                 {"tags": {"name": "Environment", "operator": "In", "values": ["UAT", "Prod"]}},
                    #             ]
                    #         },
                    #         {"dimensions": {"name": "ResourceGroup", "operator": "In", "values": ["API"]}},
                    #     ]
                    # },
                    "aggregation": {
                        "totalCost": {
                            "name": "Cost",
                            "function": "Sum"
                        }
                    },
                    "granularity": "Monthly",
                },
                "timeframe": "Custom",
                "timePeriod": {
                    "from": start_date,
                    "to": end_date
                },
                "type": "Usage",
                "grouping": [
                    {
                        "type": "Dimension",
                        "name": "meterCategory"
                    }
                ]
            },
        )

        for row in response.rows:
            print(f"Subscription Id is: {subscription_id}, Subscription Name is {subscription_name}, Month is {row[1]}, Monthly Cost is {row[0]}")

if __name__ == "__main__":
    main()

'''
https://github.com/nathanfalke/azure-sdk-for-python/blob/main/sdk/costmanagement/azure-mgmt-costmanagement/generated_samples/customer_query_grouping_mca.py
'''