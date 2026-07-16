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
    start_time = datetime(2026, 7, 1, 8, 0, 0, tzinfo=timezone.utc)

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

        sub_client = SubscriptionClient(clientcredential)
        for sub in sub_client.subscriptions.list():
            if sub.state == "Enabled":
                monitor_client = MonitorManagementClient(clientcredential, sub.subscription_id)
                cs_client = CognitiveServicesManagementClient(clientcredential, sub.subscription_id)

                for account in cs_client.accounts.list():
                    if account.kind in FOUNDRY_KINDS:
                        print(f"Checking subscription {sub.subscription_id}, Type: {account.kind}, Azure resource: {account.name}")

                        resource_id = account.id

                        metric_name = "InputTokens,OutputTokens,cacheReadInputTokens,ephemeral5mInputTokens,ephemeral1hInputTokens"
                        metric_name += ",TotalTokens,ModelRequests"

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
                                for md in (timeseries.metadatavalues or []):
                                    if md.name.value.lower() == "modelname":
                                        model_name = md.value

                                for data in timeseries.data:
                                    if data.total is not None:
                                        utc_time = data.time_stamp.replace(tzinfo=utc)
                                        beijing_time = utc_time.astimezone(beijing_tz)
                                        beijing_time_str = beijing_time.strftime("%Y-%m-%d %H:%M:%S")

                                        out(
                                            sub.display_name,
                                            sub.subscription_id,
                                            account.name,
                                            account.location,
                                            model_name,
                                            metric.name.localized_value,
                                            beijing_time_str,
                                            data.total,
                                        )

    print(f"\n结果已保存到: {out_name}")


if __name__ == "__main__":
    main()
