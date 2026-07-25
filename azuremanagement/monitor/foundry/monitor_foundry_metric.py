import os
import sys
import time
import csv
from datetime import datetime, timezone, timedelta
import pytz

from azure.core.credentials import AccessToken
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.cognitiveservices import CognitiveServicesManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.core.exceptions import HttpResponseError
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest, QueryRequestOptions, ResultFormat


class StaticTokenCredential:
    """用已有的 access_token 直接充当凭据（不做刷新）。"""
    def __init__(self, token, expires_on=None):
        self._token = token
        self._expires_on = expires_on or int(time.time()) + 3600

    def get_token(self, *scopes, **kwargs):
        return AccessToken(self._token, self._expires_on)


def main():
    # access_token 可以通过 Azure CLI 获取：
    # az account get-access-token

    access_token = ""
    clientcredential = StaticTokenCredential(access_token)

    #如果是service principal访问的，请先设置Service Principal的权限为reader
    # tenant_id = ""
    # client_id = ""
    # client_secret = ""
    #clientcredential = ClientSecretCredential(tenant_id, client_id, client_secret)


    get_foundry_monitor_metrics(clientcredential)


FOUNDRY_KINDS = {"AIServices", "OpenAI", "AIHub"}


def get_foundry_monitor_metrics(clientcredential):
    now = datetime.now(timezone.utc)

    # 2026年7月1日 08:00:00 UTC
    start_time = datetime(2026, 7, 16, 8, 0, 0, tzinfo=timezone.utc)

    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")
    timespan = f"{start_time_str}/{end_time_str}"

    utc = pytz.utc
    beijing_tz = pytz.timezone("Asia/Shanghai")

    out_name = "foundry_metrics_" + datetime.now(beijing_tz).strftime("%Y%m%d_%H%M%S") + ".csv"

    with open(out_name, "w", encoding="utf-8-sig", newline="") as out_file:
        csv_writer = csv.writer(out_file)

        csv_writer.writerow([
            "Subscription Name",
            "Subscription ID",
            "Foundry Name",
            "Location",
            "ModelName",
            "Resource Metric",
            "Beijing Time",
            "Value",
        ])

        def out(subscription_name, subscription_id, foundry_name, location, model_name, metric_name, beijing_time_str, value):
            row = [
                subscription_name,
                subscription_id,
                foundry_name,
                location,
                model_name,
                metric_name,
                beijing_time_str,
                value,
            ]
            print(row)
            csv_writer.writerow(row)
            out_file.flush()


        # SubscriptionClient 仅用于取得 Resource Graph 查询范围
        sub_client = SubscriptionClient(clientcredential)

        enabled_subscriptions = {
            sub.subscription_id: sub.display_name
            for sub in sub_client.subscriptions.list()
            if str(sub.state).lower() == "enabled"
        }

        subscription_ids = list(enabled_subscriptions.keys())

        # 使用 Azure Resource Graph 一次查询所有订阅中的 Foundry 资源
        graph_client = ResourceGraphClient(clientcredential)

        graph_query = """
        Resources
        | where type =~ "microsoft.cognitiveservices/accounts"
        | where kind in~ ("AIServices", "OpenAI", "AIHub")
        | project
            subscriptionId,
            foundryName = name,
            location,
            kind,
            resourceId = id
        | order by subscriptionId asc, foundryName asc
        """

        request = QueryRequest(
            subscriptions=subscription_ids,
            query=graph_query
        )

        foundry_resources = []

        # 处理 Resource Graph 分页
        while True:
            response = graph_client.resources(request)
            foundry_resources.extend(response.data or [])

            if not response.skip_token:
                break

            request.options.skip_token = response.skip_token

        print(
            f"Resource Graph 找到 "
            f"{len(foundry_resources)} 个 Foundry 资源"
        )

        monitor_clients = {}

        for account in foundry_resources:
            subscription_id = account["subscriptionId"]
            subscription_name = enabled_subscriptions.get(
                subscription_id,
                subscription_id,
            )

            foundry_name = account["foundryName"]
            location = account["location"]
            account_kind = account["kind"]
            resource_id = account["resourceId"]

            print(
                f"Checking subscription {subscription_id}, "
                f"Type: {account_kind}, "
                f"Azure resource: {foundry_name}"
            )

            # 每个订阅复用一个 Monitor Client
            if subscription_id not in monitor_clients:
                monitor_clients[subscription_id] = (
                    MonitorManagementClient(
                        clientcredential,
                        subscription_id,
                    )
                )

            monitor_client = monitor_clients[subscription_id]

            metric_name = (
                "InputTokens,OutputTokens,"
                "cacheReadInputTokens,"
                "ephemeral5mInputTokens,"
                "ephemeral1hInputTokens,"
                "TotalTokens,ModelRequests"
            )

            aggregation = "Total"
            interval = "P1D"

            metric_result = monitor_client.metrics.list(
                resource_id,
                timespan,
                interval,
                metric_name,
                aggregation,
                None,
                None,
                filter="ModelName eq '*'",
            )

            for metric in metric_result.value:
                for timeseries in metric.timeseries:
                    model_name = None

                    for md in timeseries.metadatavalues or []:
                        if md.name.value.lower() == "modelname":
                            model_name = md.value

                    for data in timeseries.data:
                        if data.total is not None:
                            utc_time = data.time_stamp.replace(
                                tzinfo=utc
                            )
                            beijing_time = utc_time.astimezone(
                                beijing_tz
                            )
                            beijing_time_str = (
                                beijing_time.strftime(
                                    "%Y-%m-%d %H:%M:%S"
                                )
                            )

                            out(
                                subscription_name,
                                subscription_id,
                                foundry_name,
                                location,
                                model_name,
                                metric.name.localized_value,
                                beijing_time_str,
                                data.total,
                            )

    print(f"\n结果已保存到: {out_name}")


if __name__ == "__main__":
    main()
