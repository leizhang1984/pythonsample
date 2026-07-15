import os
import sys
import time
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
        # 不知道确切过期时间就给个未来值，SDK 只用它判断是否需要刷新
        self._expires_on = expires_on or int(time.time()) + 3600

    def get_token(self, *scopes, **kwargs):
        return AccessToken(self._token, self._expires_on)
    
def main():
     # 替换为你的Service Principal信息
    # tenant_id = ""
    # client_id = ""
    # client_secret = ""


    #clientcredential = ClientSecretCredential(tenant_id, client_id, client_secret)

    access_token = ""   
    clientcredential = StaticTokenCredential(access_token)
    get_foundry_monitor_metrics(clientcredential)

FOUNDRY_KINDS = {"AIServices"}

# 获得 Foundry 资源的指标
def get_foundry_monitor_metrics(clientcredential):
    now = datetime.now(timezone.utc)
    start_time = now - timedelta(hours=48)

    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time_str = now.strftime("%Y-%m-%dT%H:%M:%SZ")

    timespan = f"{start_time_str}/{end_time_str}"

    # 设置时区信息
    utc = pytz.utc
    beijing_tz = pytz.timezone('Asia/Shanghai')

    # 以当前北京时间命名输出文件
    out_name = "foundry_metrics_" + datetime.now(beijing_tz).strftime("%Y%m%d_%H%M%S") + ".txt"

    with open(out_name, "w", encoding="utf-8") as out_file:

        def out(msg):
            print(msg)                    # 屏幕
            out_file.write(msg + "\n")    # 文件
            out_file.flush()

        sub_client = SubscriptionClient(clientcredential)
        for sub in sub_client.subscriptions.list():
            if sub.state == "Enabled":
                monitor_client = MonitorManagementClient(clientcredential, sub.subscription_id)
                cs_client = CognitiveServicesManagementClient(clientcredential, sub.subscription_id)

                for account in cs_client.accounts.list():
                    # out(f"Checking account: {account.name} in subscription {sub.subscription_id}")
                    if account.kind in FOUNDRY_KINDS:
                        # out(f"Found Foundry resource: {account.name} in subscription {sub.subscription_id}")

                        resource_id = account.id

                        # https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-cognitiveservices-accounts-metrics
                        metric_name = "InputTokens,OutputTokens,cacheReadInputTokens,ephemeral5mInputTokens,ephemeral1hInputTokens"
                        aggregation = "Total"

                        # PT1H = 1小时的时间间隔
                        interval = "PT1H"

                        metric_result = monitor_client.metrics.list(
                            resource_id, timespan, interval, metric_name, aggregation,
                            None, None, filter="ModelName eq '*'",
                        )

                        # 遍历 metric_result 中的所有值
                        for metric in metric_result.value:
                            for timeseries in metric.timeseries:
                                # 从维度元数据里取出 ModelName（服务器动态返回）
                                model_name = None
                                for md in (timeseries.metadatavalues or []):
                                    if md.name.value.lower() == "modelname":
                                        model_name = md.value
                                for data in timeseries.data:
                                    if data.total is not None:
                                        # data.time_stamp 已经是 datetime 对象，直接做时区转换
                                        utc_time = data.time_stamp.replace(tzinfo=utc)
                                        beijing_time = utc_time.astimezone(beijing_tz)
                                        beijing_time_str = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
                                        out(f"Found Foundry Name: {account.name}, "
                                            f"resource metric: {metric.name.localized_value}, "
                                            f"模型: {model_name}, 北京时间是:{beijing_time_str}, "
                                            f"当时的值是:{data.total} ")

    print(f"\n结果已保存到: {out_name}")



     
if __name__ == "__main__":
    main()