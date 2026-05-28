import os
import re
import json
import argparse
from datetime import datetime, timedelta

import pytz
from openai import OpenAI

from azure.identity import ClientSecretCredential
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest
from azure.mgmt.resourcehealth import ResourceHealthMgmtClient


# =========================================================
# 环境变量
# =========================================================
AZURE_TENANT_ID = os.getenv("AZURE_TENANT_ID")
AZURE_CLIENT_ID = os.getenv("AZURE_CLIENT_ID")
AZURE_CLIENT_SECRET = os.getenv("AZURE_CLIENT_SECRET")

AZURE_OPENAI_ENDPOINT = os.getenv("AZURE_OPENAI_ENDPOINT")
AZURE_OPENAI_API_KEY = os.getenv("AZURE_OPENAI_API_KEY")
AZURE_OPENAI_MODEL = os.getenv("AZURE_OPENAI_MODEL", "gpt-5.5")


# =========================================================
# 校验环境变量
# =========================================================
required_envs = {
    "AZURE_TENANT_ID": AZURE_TENANT_ID,
    "AZURE_CLIENT_ID": AZURE_CLIENT_ID,
    "AZURE_CLIENT_SECRET": AZURE_CLIENT_SECRET,
    "AZURE_OPENAI_ENDPOINT": AZURE_OPENAI_ENDPOINT,
    "AZURE_OPENAI_API_KEY": AZURE_OPENAI_API_KEY,
}

missing = [k for k, v in required_envs.items() if not v]

if missing:
    raise Exception(f"缺少环境变量: {', '.join(missing)}")


# =========================================================
# OpenAI Client
# =========================================================
openai_client = OpenAI(
    base_url=AZURE_OPENAI_ENDPOINT,
    api_key=AZURE_OPENAI_API_KEY
)


# =========================================================
# 命令行参数
# =========================================================
parser = argparse.ArgumentParser(
    description="Azure VM 智能故障诊断工具"
)

parser.add_argument(
    "-q",
    "--query",
    required=True,
    help="自然语言问题"
)

args = parser.parse_args()

USER_QUERY = args.query


# =========================================================
# Azure Credential
# =========================================================
credential = ClientSecretCredential(
    AZURE_TENANT_ID,
    AZURE_CLIENT_ID,
    AZURE_CLIENT_SECRET
)


# =========================================================
# AI 提取问题信息
# =========================================================
def extract_query_info(query: str):
    messages = [
        {
            "role": "system",
            "content": """
你是 Azure SRE 助手。

请从用户问题中提取：

1. private_ip
2. issue_time_beijing
3. issue_time_utc

返回 JSON：

{
  "private_ip": "",
  "issue_time_beijing": "",
  "issue_time_utc": ""
}

要求：

1. 北京时间必须符合 ISO8601
2. UTC 时间格式:
   YYYY-MM-DDTHH:MM:SSZ
3. 如果用户没有提到时间，使用北京时间最近一小时（即当前时间往前推1小时）
4. 不允许返回 markdown
5. 仅返回 JSON
"""
        },
        {
            "role": "user",
            "content": query
        }
    ]

    response = openai_client.chat.completions.create(
        model=AZURE_OPENAI_MODEL,
        messages=messages,
#         temperature=1
    )

    content = response.choices[0].message.content.strip()

    data = json.loads(content)

    return data


# =========================================================
# 通过IP查询虚拟机
# =========================================================
def get_vm_by_private_ip(private_ip: str):
    subscription_client = SubscriptionClient(credential)

    subscriptions = [
        sub.subscription_id
        for sub in subscription_client.subscriptions.list()
    ]

    resourcegraph_client = ResourceGraphClient(credential)

    query = QueryRequest(
        query=f"""
Resources
| where type =~ 'microsoft.network/networkinterfaces'
| mv-expand ipconfig = properties.ipConfigurations
| extend
    vmId = tolower(tostring(properties.virtualMachine.id)),
    privateIp = tostring(ipconfig.properties.privateIPAddress)
| where privateIp == '{private_ip}'
| join kind=inner (
    Resources
    | where type =~ 'microsoft.compute/virtualmachines'
    | extend vmId = tolower(tostring(id))
    | project
        vmId,
        subscriptionId,
        vmName = name,
        resourceGroup,
        vmSize = tostring(properties.hardwareProfile.vmSize),
        location
) on vmId
| project
    vmId,
    subscriptionId,
    vmName,
    resourceGroup,
    vmSize,
    location,
    privateIp
""",
        subscriptions=subscriptions
    )

    response = resourcegraph_client.resources(query)

    if response.count == 0:
        raise Exception(f"没有找到 IP 为 {private_ip} 的虚拟机")

    vm = response.data[0]

    return {
        "vm_id": vm["vmId"],
        "subscription_id": vm["subscriptionId"],
        "vm_name": vm["vmName"],
        "resource_group": vm["resourceGroup"],
        "vm_size": vm["vmSize"],
        "location": vm["location"],
        "private_ip": vm["privateIp"]
    }


# =========================================================
# Activity Log
# =========================================================
def get_activity_logs(
        subscription_id: str,
        vm_id: str,
        issue_time_iso: str
):
    monitor_client = MonitorManagementClient(
        credential,
        subscription_id
    )

    issue_time = datetime.fromisoformat(issue_time_iso)

    start_time = issue_time - timedelta(minutes=30)
    end_time = issue_time + timedelta(minutes=30)

    filter_query = (
        f"eventTimestamp ge '{start_time.isoformat()}' "
        f"and eventTimestamp le '{end_time.isoformat()}' "
        f"and resourceId eq '{vm_id}'"
    )

    logs = monitor_client.activity_logs.list(
        filter=filter_query
    )

    result = []

    for log in logs:
        result.append({
            "event_time": str(log.event_timestamp),
            "operation_name":
                log.operation_name.localized_value
                if log.operation_name else None,
            "status":
                log.status.localized_value
                if log.status else None,
            "caller": log.caller,
            "level": log.level,
            "category":
                log.category.localized_value
                if log.category else None
        })

    return result


# =========================================================
# Resource Health
# =========================================================
def get_resource_health_events(
        subscription_id: str,
        vm_id: str
):
    client = ResourceHealthMgmtClient(
        credential,
        subscription_id
    )

    result = []

    try:
        response = client.events.list_by_single_resource(
            vm_id
        )

        for item in response:
            result.append({
                "title": item.title,
                "summary": item.summary,
                "reason": item.reason,
                "impact_start_time":
                    str(item.impact_start_time),
                "status": item.status
            })

    except Exception as e:
        result.append({
            "error": str(e)
        })

    return result


# =========================================================
# Metrics
# =========================================================
def get_vm_metrics(
        subscription_id: str,
        vm_id: str,
        issue_time_iso: str
):
    monitor_client = MonitorManagementClient(
        credential,
        subscription_id
    )

    metrics = [
        "Percentage CPU",
        "Available Memory Percentage",
        "VmAvailabilityMetric",
        "OS Disk Bandwidth Consumed Percentage",
        "OS Disk IOPS Consumed Percentage",
        "Data Disk Bandwidth Consumed Percentage",
        "Data Disk IOPS Consumed Percentage",
        "OS Disk Queue Depth",
        "Data Disk Queue Depth",
        "VM Uncached Bandwidth Consumed Percentage",
        "VM Uncached IOPS Consumed Percentage",
        "OS Disk Latency",
        "Data Disk Latency"
    ]

    issue_time = datetime.fromisoformat(issue_time_iso)

    utc_time = issue_time.astimezone(pytz.utc)

    start_time = utc_time - timedelta(minutes=30)
    end_time = utc_time + timedelta(minutes=30)

    timespan = (
        f"{start_time.strftime('%Y-%m-%dT%H:%M:%SZ')}/"
        f"{end_time.strftime('%Y-%m-%dT%H:%M:%SZ')}"
    )

    response = monitor_client.metrics.list(
        vm_id,
        timespan=timespan,
        interval="PT5M",
        metricnames=",".join(metrics),
        aggregation="Maximum"
    )

    beijing_tz = pytz.timezone("Asia/Shanghai")

    result = []

    for metric in response.value:
        for ts in metric.timeseries:
            for data in ts.data:
                if data.maximum is None:
                    continue

                bj_time = (
                    data.time_stamp
                    .replace(tzinfo=pytz.utc)
                    .astimezone(beijing_tz)
                )

                result.append({
                    "metric_name":
                        metric.name.localized_value,
                    "timestamp":
                        bj_time.strftime(
                            "%Y-%m-%d %H:%M:%S"
                        ),
                    "maximum":
                        data.maximum
                })

    return result


# =========================================================
# AI 故障分析
# =========================================================
def analyze_vm_issue(
        user_query: str,
        vm_info: dict,
        activity_logs: list,
        resource_health: list,
        metrics: list
):
    payload = {
        "user_query": user_query,
        "vm_info": vm_info,
        "activity_logs": activity_logs,
        "resource_health": resource_health,
        "metrics": metrics
    }

    messages = [
        {
            "role": "system",
            "content": """
你是一位拥有20年以上经验的 Azure SRE / DevOps 专家。

你需要分析：

1. Azure Activity Log
2. Azure Resource Health
3. Azure VM Metrics
4. Azure Disk 性能
5. VM Availability
6. CPU / Memory / Disk Latency / IOPS

请重点识别：

1. CPU 瓶颈
2. 内存不足
3. Azure 磁盘限流
4. IOPS 超限
5. Bandwidth 超限
6. Queue Depth 异常
7. Latency 飙升
8. VM 不可用
9. Azure 平台故障
10. 短时 Burst 与持续瓶颈

输出格式：

# Azure VM 故障分析报告

## 1. 问题摘要

## 2. 关键异常指标

## 3. Activity Log 分析

## 4. Resource Health 分析

## 5. 根因分析

## 6. 风险等级

## 7. 优化建议

## 8. 最终结论

要求：

1. 必须专业
2. 必须具体
3. 必须指出时间点
4. 必须指出指标异常
5. 不允许泛泛而谈
"""
        },
        {
            "role": "user",
            "content": json.dumps(
                payload,
                ensure_ascii=False,
                indent=2
            )
        }
    ]

    response = openai_client.chat.completions.create(
        model=AZURE_OPENAI_MODEL,
        messages=messages,
#         temperature=0.2
    )

    return response.choices[0].message.content


# =========================================================
# 保存报告
# =========================================================
def save_report(report: str):
    current_time = datetime.now().strftime(
        "%Y-%m-%d-%H-%M-%S"
    )

    filename = f"azure_vm_analysis_{current_time}.md"

    # 保存到 tmp 目录，便于 oss_upload 工具上传
    tmp_dir = "/data/sre-agent-eino/tmp"
    os.makedirs(tmp_dir, exist_ok=True)
    filepath = os.path.join(tmp_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        f.write(report)

    return filepath


# =========================================================
# Main
# =========================================================
def main():
    print("\n==============================")
    print("Azure VM 智能故障诊断")
    print("==============================\n")

    # 1. AI 提取用户问题
    print("1. 正在解析用户问题...")

    extracted = extract_query_info(USER_QUERY)

    private_ip = extracted["private_ip"]
    issue_time_beijing = extracted.get("issue_time_beijing", "")
    issue_time_utc = extracted.get("issue_time_utc", "")

    # 如果用户没有指定时间，默认使用北京时间最近一小时
    if not issue_time_beijing or not issue_time_utc:
        now_beijing = datetime.now(pytz.timezone("Asia/Shanghai"))
        issue_time_beijing = now_beijing.strftime("%Y-%m-%dT%H:%M:%S+08:00")
        issue_time_utc = now_beijing.astimezone(pytz.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        print("用户未指定时间，默认使用北京时间最近一小时")

    print(f"内网IP: {private_ip}")
    print(f"北京时间: {issue_time_beijing}")
    print(f"UTC时间: {issue_time_utc}")

    # 2. 查询虚拟机
    print("\n2. 正在查询 Azure VM ...")

    vm_info = get_vm_by_private_ip(private_ip)

    print(
        f"找到虚拟机: "
        f"{vm_info['vm_name']} "
        f"({vm_info['vm_size']})"
    )

    # 3. Activity Log
    print("\n3. 正在获取 Activity Logs ...")

    activity_logs = get_activity_logs(
        vm_info["subscription_id"],
        vm_info["vm_id"],
        issue_time_beijing
    )

    print(f"获取到 {len(activity_logs)} 条日志")

    # 4. Resource Health
    print("\n4. 正在获取 Resource Health ...")

    resource_health = get_resource_health_events(
        vm_info["subscription_id"],
        vm_info["vm_id"]
    )

    print(f"获取到 {len(resource_health)} 条健康事件")

    # 5. Metrics
    print("\n5. 正在获取 VM Metrics ...")

    metrics = get_vm_metrics(
        vm_info["subscription_id"],
        vm_info["vm_id"],
        issue_time_beijing
    )

    print(f"获取到 {len(metrics)} 条指标")

    # 6. AI 分析
    print("\n6. 正在进行 AI 根因分析 ...")

    report = analyze_vm_issue(
        USER_QUERY,
        vm_info,
        activity_logs,
        resource_health,
        metrics
    )

    # 7. 保存报告（先保存，这样即使输出被截断，agent 也知道文件位置）
    filename = save_report(report)

    print(f"\n报告已保存: {filename}")
    print("\n================ 分析结果 ================\n")

    # 8. 输出报告（可能会超过 5000 字符被截断）
    print(report)


# =========================================================
# Entry
# =========================================================
if __name__ == "__main__":
    main()