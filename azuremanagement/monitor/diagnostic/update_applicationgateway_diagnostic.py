import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.monitor import MonitorManagementClient
from azure.mgmt.monitor.models import DiagnosticSettingsResource
from azure.mgmt.eventhub import EventHubManagementClient
from azure.eventhub import EventHubProducerClient, EventData


# 设置环境变量以便使用 ClientSecretCredential
tenantid = os.environ.get('nonprod_tenantid')
clientid = os.environ.get('nonprod_clientid')
clientsecret = os.environ.get('nonprod_clientsecret')

subscription_id = '166157a8-9ce9-400b-91c7-1d42482b83d6'
# Application Gateway所在的资源组名称
resource_group_name = 'FW-Hybrid-Test'
application_gateway_name = 'leiappgw01'

# Event Hub所在资源组名称
event_hub_resource_group_name = 'lab-rg'
event_hub_namespace = 'azuremonitorns'
event_hub_name = 'resourcehealth'


clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

# 创建 NetworkManagementClient 和 MonitorManagementClient
network_client = NetworkManagementClient(clientcredential, subscription_id)
monitor_client = MonitorManagementClient(clientcredential, subscription_id)
eventhub_client = EventHubManagementClient(clientcredential, subscription_id)

# 获取 Application Gateway 资源 ID
application_gateway = network_client.application_gateways.get(resource_group_name, application_gateway_name)
application_gateway_id = application_gateway.id


# 获取 Event Hub Authorization Rule ID
# 默认有1个RootManageSharedAccessKey
auth_rule = eventhub_client.namespaces.get_authorization_rule(
    event_hub_resource_group_name,
    event_hub_namespace,
    "RootManageSharedAccessKey"
)

event_hub_authorization_rule_id = auth_rule.id


# 配置诊断设置
diagnostic_settings = DiagnosticSettingsResource(
    storage_account_id=None,
    event_hub_authorization_rule_id=event_hub_authorization_rule_id,
    event_hub_name=event_hub_name,
    logs=[
        {
            "category_group": "allLogs",
            "enabled": True,
            "retentionPolicy": {
                "enabled": False,
                "days": 0
            }
        }
    ],
    metrics=[
        {
            "category": "AllMetrics",
            "enabled": True,
            "retentionPolicy": {
                "enabled": False,
                "days": 0
            }
        }
    ]
)

#创建或更新诊断设置
response = monitor_client.diagnostic_settings.create_or_update(
    resource_uri=application_gateway_id,
    name='application-gateway-diagnostics',
    parameters=diagnostic_settings
)

response = monitor_client.diagnostic_settings.get(resource_uri=application_gateway_id, name='application-gateway-diagnostics')

print(response)
print("Diagnostic settings configured successfully.")

'''
上面的sample是
    logs=[
        {
            "category_group": "allLogs",
            "enabled": True,
            "retentionPolicy": {
                "enabled": False,
                "days": 0
            }
        }
    ],
包含所有的Log

如果要指定某些Logs, 请参考下面的参数
diagnostic_settings = DiagnosticSettingsResource(
    storage_account_id=None,
    event_hub_authorization_rule_id=event_hub_authorization_rule_id,
    event_hub_name=event_hub_name,
    logs=[
        {
            "category": "ApplicationGatewayAccessLog",
            "enabled": True,
            "retentionPolicy": {
                "enabled": False,
                "days": 0
            }
        },
        {
            "category": "ApplicationGatewayPerformanceLog",
            "enabled": True,
            "retentionPolicy": {
                "enabled": False,
                "days": 0
            }
        },
        {
            "category": "ApplicationGatewayFirewallLog",
            "enabled": True,
            "retentionPolicy": {
                "enabled": False,
                "days": 0
            }
        }
    ],
    metrics=[
        {
            "category": "AllMetrics",
            "enabled": True,
            "retentionPolicy": {
                "enabled": False,
                "days": 0
            }
        }
    ]
)

'''