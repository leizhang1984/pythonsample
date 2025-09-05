import os
import re
from datetime import datetime, timedelta
import pytz
from openai import AzureOpenAI
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.resourcehealth import ResourceHealthMgmtClient
from azure.mgmt.resource import SubscriptionClient
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.resource import ResourceManagementClient
from dateutil import parser

input_prompt = ""

#在这里描述问题
default_prompt = "请帮我找内网为10.99.76.10这台虚拟机,在北京时间2025年9月2日下午3点10分有没有问题。"

# 通过内网ip，获得虚拟机的资源id，资源组和虚拟机名称
def get_vm_resource_graph_byip(tenant_id, client_id, client_secret, private_ip_address):

    clientcredential = ClientSecretCredential(tenant_id, client_id, client_secret)

    # Create SubscriptionClient to list all accessible subscriptions
    subscription_client = SubscriptionClient(clientcredential)
    subscriptions = [sub.subscription_id for sub in subscription_client.subscriptions.list()]

    # Create ResourceGraphClient
    resourcegraph_client = ResourceGraphClient(credential=clientcredential)

    while True:
        # Basic query
        query = QueryRequest(
            query=f'''Resources
                        | where type =~ 'microsoft.compute/virtualmachines'
                        | project subscriptionId, vmId = tolower(tostring(id)), vmName = name, resourceGroup = resourceGroup
                        | join (Resources
                            | where type =~ 'microsoft.network/networkinterfaces'
                            | mv-expand ipconfig=properties.ipConfigurations
                            | project vmId = tolower(tostring(properties.virtualMachine.id)), 
                                    privateIp = ipconfig.properties.privateIPAddress, 
                                    publicIpId = tostring(ipconfig.properties.publicIPAddress.id)
                            | join kind=leftouter (Resources
                                | where type =~ 'microsoft.network/publicipaddresses'
                                | project publicIpId = id, publicIp = properties.ipAddress
                            ) on publicIpId
                            | project-away publicIpId, publicIpId1
                            | summarize privateIps = make_list(privateIp), publicIps = make_list(publicIp) by vmId
                        ) on vmId
                        | project  vmId,subscriptionId, vmName, resourceGroup, privateIps, publicIps
                        | where privateIps contains '{private_ip_address}'
                        | sort by vmName asc ''',
            subscriptions=subscriptions
        )

        query_response = resourcegraph_client.resources(query)
        
        if query_response.count == 0:
            print(f"没有找到虚拟机内网IP为 {private_ip_address} 的虚拟机，请重新输入")
            private_ip_address = input("请输入新的内网IP地址：")
        elif query_response.count == 1:
            return (
                query_response.data[0]['vmId'],
                query_response.data[0]['subscriptionId'],
                query_response.data[0]['vmName'],
                query_response.data[0]['resourceGroup'],
                query_response.data[0]['privateIps']
            )
        else:
            print(f"找到多台虚拟机，内网IP都是 {private_ip_address}")
            # 遍历结果并打印
            for idx, result in enumerate(query_response.data, 1):
                print(f"第{idx}台虚拟机, 订阅名称是: {result['vmName']}, Resource Group: {result['resourceGroup']}, VM Name: {result['vmName']}, Private IPs: {result['privateIps']}")
            
            # 让用户选择其中一个虚拟机
            while True:
                try:
                    choice = int(input("请选择要使用的虚拟机编号（输入数字）："))
                    if 1 <= choice <= query_response.count:
                        result = query_response.data[choice - 1]
                        return (
                            result['vmId'],
                            result['subscriptionId'],
                            result['vmName'],
                            result['resourceGroup'],
                            result['privateIps']
                        )
                    else:
                        print("输入的编号无效，请重新选择")
                except ValueError:
                    print("输入的不是有效的数字，请重新选择")

#获得VM的活动日志
def get_vm_activity_log(tenant_id, client_id, client_secret,subscription_id, rg_name, vm_name, vm_id, issue_time_str):
    # 使用ClientSecretCredential进行身份验证
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)

     # 创建 MonitorManagementClient 实例
    monitor_client = MonitorManagementClient(credential, subscription_id)
    
     # 创建 ResourceManagementClient 实例
    resource_client = ResourceManagementClient(credential, subscription_id)

    # 解析带有时区信息的字符串为 datetime 对象
    issue_time = datetime.fromisoformat(issue_time_str)

    # 计算前30分钟
    start_time = issue_time - timedelta(minutes=30)
    start_time_str = start_time.isoformat()

    #计算后30分钟
    end_time =  issue_time + timedelta(minutes=30)
    end_time_str = end_time.isoformat()

    # 构建查询过滤器
    filter_query = f"eventTimestamp ge '{start_time_str}' and eventTimestamp le '{end_time_str}' and resourceId eq '{vm_id}'"

    # 获取活动日志
    activity_logs = monitor_client.activity_logs.list(filter=filter_query)

    # 打印活动日志
    for log in activity_logs:
        global input_prompt
        input_prompt += f"在时间: {log.event_timestamp}, 发现虚拟机的活动日志: {log.operation_name.localized_value}, 执行状态是: {log.status.localized_value} "


                
#获得VM的Resource Health
def get_vm_resource_health(tenant_id, client_id, client_secret,subscription_id, rg_name, vm_name, vm_id):
    # 使用ClientSecretCredential进行身份验证
    credential = ClientSecretCredential(tenant_id, client_id, client_secret)

    # 创建计算管理客户端
    compute_client = ComputeManagementClient(credential, subscription_id)

    # 获取虚拟机的详细信息
    try:
        #vm = compute_client.virtual_machines.get(resource_group_name, vm_name)
        resource_id = vm_id
        print(f"Resource ID: {resource_id}")
    except Exception as e:
        print(f"Error retrieving VM details for '{vm_name}': {e}")
        return

    # 创建Resource Health管理客户端
    resource_health_client = ResourceHealthMgmtClient(credential, subscription_id)

    try:

        response = resource_health_client.events.list_by_single_resource(resource_id)
        for item in response:
            #print(f"Time is {item.impact_start_time}, Reason is {item.reason}, Title is {item.title}, summary is {item.summary}")
            global input_prompt
            input_prompt+= f"发现虚拟机的Resource Health，在时间{item.impact_start_time}, 遇到事件 {item.summary}"

    except Exception as e:
        print(f"Error retrieving resource health for VM '{vm_name}': {e}")

#获得虚拟机的指标
def get_vm_monitor_metrics(tenant_id, client_id, client_secret,subscription_id, rg_name, vm_name, vm_id, issue_time_str):
    clientcredential = ClientSecretCredential(tenant_id,client_id,client_secret)
    compute_client = ComputeManagementClient(clientcredential, subscription_id)
    monitor_client = MonitorManagementClient(clientcredential, subscription_id)

    #获得虚拟机的信息
    #vm = compute_client.virtual_machines.get(resource_group_name,vm_name)
    resource_id = vm_id
    #把客户上报的时间，改为ISO格式
    #解析时间字符串为 datetime 对象
    original_time = datetime.fromisoformat(issue_time_str)

    # 将时间转换为 UTC
    utc_time = original_time.astimezone(pytz.utc)

    # 计算开始时间，这里假设结束时间是开始时间，减少30 minutes
    # start_time = utc_time + timedelta(hours=-1)
    start_time = utc_time + timedelta(minutes=-30)

    # 计算结束时间，这里假设结束时间是开始时间加30 minutes
    end_time = utc_time + timedelta(minutes=30)

    # 格式化为所需的字符串格式
    start_time_str = start_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    end_time_str = end_time.strftime("%Y-%m-%dT%H:%M:%SZ")
    
    # 拼接成最终的格式
    timespan = f"{start_time_str}/{end_time_str}"
    #timespan = '2025-04-11T08:38:00Z/2025-04-11T09:00:00Z'

    #虚拟机的指标值
    #https://learn.microsoft.com/en-us/azure/azure-monitor/reference/supported-metrics/microsoft-compute-virtualmachines-metrics


    #internal PT1H 代表每1小时,目前只支持1小时抽样间隔
    #internal PT1M 代表每1分钟

    #Percentage CPU	                代表CPU利用率
    #Available Memory Percentage    代表可用内存百分比
    #Network In Total               代表入向流量
    #Network Out Total              代表出向流量

    #Bandwidth Consumed Percentage  代表消耗的带宽百分比

    #Queue Depth                    代表队列深度
    metric_name = "Percentage CPU,Available Memory Percentage,VmAvailabilityMetric"
    metric_name += ",OS Disk Bandwidth Consumed Percentage,OS Disk IOPS Consumed Percentage"
    metric_name += ",Data Disk Bandwidth Consumed Percentage,Data Disk IOPS Consumed Percentage"
    metric_name += ",OS Disk Queue Depth,Data Disk Queue Depth"

    #aggregation = "average,total"
    aggregation = "Maximum"

    #metric_result = monitor_client.metrics.list(resource_id,timespan,"PT5M",metric_name,aggregation,None,None,None)
    metric_result = monitor_client.metrics.list(resource_id,timespan,"PT5M",metric_name,aggregation,None,None,None)

    # 设置时区信息
    utc = pytz.utc
    beijing_tz = pytz.timezone('Asia/Shanghai')

    # 遍历 metric_result 中的所有值
    for metric in metric_result.value:
        #print(f"Metric: {metric.name.localized_value} ({metric.name.value})")
        for timeseries in metric.timeseries:
            for data in timeseries.data:
                # print(f"TimeStamp: {data.time_stamp}")
                # if data.average is not None:
                #     print(f"Average: {data.average}")
                # if data.total is not None:
                #     print(f"Total: {data.total}")
                # if data.minimum is not None:
                #     print(f"Minimum: {data.minimum}")
                if data.maximum is not None:
                    # data.time_stamp 已经是一个 datetime 对象，直接进行时区转换
                    utc_time = data.time_stamp.replace(tzinfo=utc)
                    # 转换为北京时间
                    beijing_time = utc_time.astimezone(beijing_tz)
                    # 格式化为字符串
                    beijing_time_str = beijing_time.strftime("%Y-%m-%d %H:%M:%S")
                    # print(f"Maximum: {data.maximum}")
                    global input_prompt
                    input_prompt += f"在北京时间:{beijing_time_str},发现虚拟机的监控指标:{metric.name.localized_value}, 当时的最大值是:{data.maximum}\n"

            # if data.count is no
                # if data.count is not None:
                #     print(f"Count: {data.count}")


def request_openai_final(subscription_id,rg_name,vm_name,private_ip,issue_time):
    # Initialize the Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint = os.environ.get('azure_openai_endpoint'),
        api_key = os.environ.get('azure_openai_key'),
        api_version = "2023-08-01-preview"
    )
    # 定义 prompt
    #10.100.208.4
    default_prompt = f"订阅ID为:{subscription_id}, 资源组名称为:{rg_name}, 虚拟机名称为: {vm_name}, 内网IP地址: {private_ip}, 在问题发生时间: {issue_time}"
    prompt = default_prompt + input_prompt

    # Define the messages for the chat completion
    # This structure mirrors the roles used in the Chat Playground
    messages = [
        {
            "role": "system",
            "content": (
                # "你是一位拥有超过15年经验的 Azure 资深 DevOps/SRE 专家。你的核心职责是主动确保云基础架构的性能、成本和可靠性达到最佳状态。你对 Azure IaaS，特别是虚拟机和磁盘存储的内部工作原理了如指掌。\n"
                # "你的任务是：根据我提供的 Azure 磁盘监控指标数据，进行一次全面、深入的健康状况分析。你的分析不能只停留在表面数据，必须模拟一个真实专家的思维过程：识别潜在风险、推测根本原因，并给出具体、可操作的优化建议\n"
                # "在开始分析之前，你必须牢记以下关于 Azure 磁盘性能的核心原则：\n"
                # "1.  **预配 vs. 消耗 (Provisioned vs. Consumed)**：每个 Azure 磁盘 SKU（如 Standard_LRS, Premium_P30, Ultra）都带有明确的性能目标：预配的 IOPS（每秒读写次数）和吞吐量（MB/s）。我们监控的“磁盘已用百分比”就是将实际消耗值与这个预配目标进行比较。\n"
                # "2.  **性能瓶颈与限流 (Bottleneck & Throttling)***: 当“磁盘已用 IOPS 百分比”或“磁盘已用带宽百分比”**持续**接近或达到 100% 时，意味着磁盘性能已达到其预配上限。* 一旦超过 100%，Azure 平台会开始对磁盘进行**限流 (Throttling)**。这会导致磁盘请求被强制延迟或拒绝，磁盘的平均延迟 (Latency) 会急剧上升，从而严重影响上层虚拟机和应用的性能，甚至导致应用超时或崩溃。**识别限流风险是你分析的首要任务**。\n"
                # "3.  **突发性能 (Bursting)**：某些磁盘类型（如 Standard SSD、Premium SSD v1）支持性能突发。它们可以短时间内超越预配的性能目标。在分析时，你需要区分是健康的、短暂的性能突发，还是预示着磁盘规格不足的、持续性的高负载。持续的高负载最终会耗尽突发信用点，导致更严重的限流。\n"
                # "4.  **延迟 (Latency)**：延迟是衡量磁盘健康状况的最终体现。一个健康的磁盘，其延迟应该稳定且在个位数毫秒（对于 SSD）。延迟的突然飙升，通常是高 IOPS/吞吐量导致限流的直接症状。\n"          

                "你是一位拥有超过20年经验的 Azure 资深 DevOps/SRE 专家。你的核心职责是主动确保云基础架构的性能、成本和可靠性达到最佳状态。你对 Azure IaaS，特别是虚拟机和磁盘存储的内部工作原理了如指掌。 \n"
                "你的任务是：根据我提供的 Azure 磁盘监控指标数据，进行一次全面、深入的健康状况分析。你的分析不能只停留在表面数据，必须模拟一个真实专家的思维过程：识别潜在风险、推测根本原因，并给出具体、可操作的优化建议 \n"
                "你需要根据以下提供的Azure Resource Health指标，Azure Percentage CPU (CPU利用率)，Available Memory Percentage(可用内存)，Azure VmAvailabilityMetric可用性指标 \n"
                "OS Disk Bandwidth Consumed Percentage，OS Disk IOPS Consumed Percentage，Data Disk Bandwidth Consumed Percentage, Data Disk IOPS Consumed Percentage \n"
                "发现Azure虚拟机在规定时间段内，可能产生的性能瓶颈 \n"
                
                "在开始分析之前，你必须牢记以下关于 Azure 磁盘性能的核心原则：\n"
                "1.  **预配 vs. 消耗 (Provisioned vs. Consumed)**：每个 Azure 磁盘 SKU（如 Standard_LRS, Premium_P30, Ultra）都带有明确的性能目标：预配的 IOPS（每秒读写次数）和吞吐量（MB/s）。我们监控的“磁盘已用百分比”就是将实际消耗值与这个预配目标进行比较。\n"
                "2.  **性能瓶颈与限流 (Bottleneck & Throttling)***: 当“磁盘已用 IOPS 百分比”或“磁盘已用带宽百分比”**持续**接近或达到 100% 时，意味着磁盘性能已达到其预配上限。* 一旦超过 100%，Azure 平台会开始对磁盘进行**限流 (Throttling)**。这会导致磁盘请求被强制延迟或拒绝，磁盘的平均延迟 (Latency) 会急剧上升，从而严重影响上层虚拟机和应用的性能，甚至导致应用超时或崩溃。**识别限流风险是你分析的首要任务**。\n"
                "3.  **突发性能 (Bursting)**：某些磁盘类型（如 Standard SSD、Premium SSD v1）支持性能突发。它们可以短时间内超越预配的性能目标。在分析时，你需要区分是健康的、短暂的性能突发，还是预示着磁盘规格不足的、持续性的高负载。持续的高负载最终会耗尽突发信用点，导致更严重的限流。\n"
                "4.  **延迟 (Latency)**：延迟是衡量磁盘健康状况的最终体现。一个健康的磁盘，其延迟应该稳定且在个位数毫秒（对于 SSD）。延迟的突然飙升，通常是高 IOPS/吞吐量导致限流的直接症状。\n"       
                
                "回复的内容必须遵循以下格式：\n"
                f"第1部分，问题描述: {default_prompt} \n"
                
                "第2部分，关键性能指标。发现在时间段yyyy-mm-dd mm:ss，检查内网ip为xxx.xxx.xxx.xxx的虚拟机，检查Azure活动日志Activity Log，发现日志是： \n"
                "这里提供规定时间范围内，所有的活动日志Activity Log的总结 \n"

                "检查Azure Resource Health，发现日志是： \n"
                "这里提供规定时间范围内，所有的Azure Resource Health内容，可以支持多行 \n"

                "发现虚拟机的监控指标： \n"
                "这里详细描述问题发生的前30分钟到后30分钟，每一个Azure性能指标，包含时间，指标名称，最大值，可以支持多行数据 \n"
                "如果是一个新的指标值，请单独插入一个空行 \n"

                "第3部分.根据目前的性能指标，发现可能存在的性能瓶颈和问题是： \n"
                "第4部分.优化建议是 \n"
                "第5部分.结论是在这个时间段内有发现性能问题，主要问题是:xxxxx，建议的方案是。或者没有发现性能问题xxxx \n"
            )
        },
        {"role": "user", "content": f"{prompt}"}
    ]

    response = client.chat.completions.create(
        model = "gpt-4.1",  # Replace with your deployed model name
        messages = messages,
        #temperature = 0.7,  # Optional: Controls randomness of output
        #max_tokens = 150    # Optional: Limits the length of the response
    )

    response_content  = response.choices[0].message.content
    print(response_content)

    # 获取当前时间并格式化为字符串
    current_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    file_name = f"output_{current_time}.txt"

    # 打开文件并写入内容
    with open(file_name, "w", encoding="utf-8") as file:
        file.write(response_content)

    print(f"内容已导出到 {file_name}")
    


def request_openai():
    # Initialize the Azure OpenAI client
    client = AzureOpenAI(
        azure_endpoint = os.environ.get('azure_openai_endpoint'),
        api_key = os.environ.get('azure_openai_key'),
        api_version = "2023-08-01-preview"
    )
    # 定义 prompt
    #10.100.208.4
    global default_prompt
    prompt = default_prompt + "需要帮我把这句话提取关键信息，把内网ip并返回在<privateip></privateip>，请把时间转换为北京时间， 符合ISO 8601 标准,并返回在<issuetime></issuetime>"

    # Define the messages for the chat completion
    # This structure mirrors the roles used in the Chat Playground
    messages = [
         {"role": "system", "content": "You are a helpful assistant."},
         {"role": "user", "content": f"{prompt}"}
    ]

    response = client.chat.completions.create(
        model = "gpt-4.1",  # Replace with your deployed model name
        messages = messages,
        #temperature = 0.7,  # Optional: Controls randomness of output
        #max_tokens = 150    # Optional: Limits the length of the response
    )

    response_content  = response.choices[0].message.content
    # 使用正则表达式提取 <privateip> 和 <issuetime> 中的值
    private_ip = re.search(r'<privateip>(.*?)</privateip>', response_content).group(1)
    #print(f"{private_ip}")
    issue_time = re.search(r'<issuetime>(.*?)</issuetime>', response_content).group(1)
    #print(f"{issue_time}")

    return private_ip, issue_time

def main():
     # 替换为你的Service Principal信息
    tenant_id = os.environ.get('nonprod_tenantid')
    client_id = os.environ.get('nonprod_clientid')
    client_secret = os.environ.get('nonprod_clientsecret')


    private_ip, issue_time = request_openai()
    vm_id, subscription_id,vm_name, rg_name, private_ip = get_vm_resource_graph_byip(tenant_id, client_id, client_secret, private_ip)
    get_vm_activity_log(tenant_id,client_id,client_secret,subscription_id,rg_name,vm_name,vm_id,issue_time)
    get_vm_resource_health(tenant_id,client_id,client_secret,subscription_id,rg_name,vm_name,vm_id)
    get_vm_monitor_metrics(tenant_id,client_id,client_secret,subscription_id,rg_name,vm_name,vm_id,issue_time)
    request_openai_final(subscription_id,rg_name,vm_name,private_ip,issue_time)

if __name__ == "__main__":
    main()