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
        subscription_id = subscription.subscription_id
        subscription_name = subscription.display_name


        # 发送生成报告的请求
        response = cost_mgmt_client.generate_cost_details_report.begin_create_operation(
            scope = f"subscriptions/{subscription_id}",  
            parameters = GenerateCostDetailsReportRequestDefinition(
            metric = CostDetailsMetricType.ACTUAL_COST_COST_DETAILS_METRIC_TYPE,
            # metric=CostDetailsMetricType.ACTUAL_COST_COST_DETAILS_METRIC_TYPE, AMORTIZED_COST_COST_DETAILS_METRIC_TYPE
            time_period = CostDetailsTimePeriod(
                start = start_date,
                end = end_date
            )
          )
        ).result()


        # 检查 response.status 并等待直到 status 为 "Completed"
        while response.status != "Completed":
            print("Report generation in progress. Waiting for 30 seconds...")
            time.sleep(30)
            # 重新获取 response 状态（假设有方法可以重新获取状态）
            response = cost_mgmt_client.generate_cost_details_report.get_operation_status(response.operation_id)

        print("Report generation completed. Continuing with the next steps.")
        blob_link = response.blobs[0].blob_link

        print(f"Subscription Name: {subscription_name}")
        print(f"Subscription ID: {subscription_id}")
        print(f"Blob Link: {blob_link}")


if __name__ == "__main__":
    main()
