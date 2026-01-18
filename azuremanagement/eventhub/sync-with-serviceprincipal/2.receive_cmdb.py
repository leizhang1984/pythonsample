import os
import json
import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
from azure.identity.aio import ClientSecretCredential as AioClientSecretCredential
from azure.identity import ClientSecretCredential  # 用于同步的 ResourceManagementClient
from azure.mgmt.resource import ResourceManagementClient  # 需要安装 azure-mgmt-resource 包

from azure.mgmt.compute import ComputeManagementClient

# Event Hub 配置
eventhub_namespace = "azuremonitorns.servicebus.windows.net"  # os.getenv("EVENT_HUB_NAMESPACE")
eventhub_name = "azuresubscription"  # os.getenv("EVENT_HUB_NAME")
consumer_group = "pythonclient"  # 需要提前创建好：consumer_group

# Blob 存储配置
blob_storage_account_url = 'https://azuremonitorns01.blob.core.windows.net'  # os.getenv('BLOB_STORAGE_ACCOUNT_URL')
blob_container_name = 'azuresubscription'  # os.getenv('BLOB_CONTAINER_NAME')

# 服务主体（Service Principal）配置
tenantid = os.environ.get('nonprod_tenantid')
clientid = os.environ.get('nonprod_clientid')
clientsecret = os.environ.get('nonprod_clientsecret')

# 创建异步和同步的 ClientSecretCredential
async_credential = AioClientSecretCredential(tenantid, clientid, clientsecret)
sync_credential = ClientSecretCredential(tenantid, clientid, clientsecret)

async def on_event(partition_context, event):
    # print("======================================================")
    # print("======================================================")
    # print("======================================================")
    print("Received event from partition: {}.".format(partition_context.partition_id))
    print(f"Data: {event.body_as_str()}")

    # 解析事件数据
    event_data_str = event.body_as_str()
    event_data = json.loads(event_data_str)
    
    # 提取所需字段
    for item in event_data:
        resource_provider = item.get('data', {}).get('resourceProvider', 'Resource Provider not found')
        resource_uri = item.get('data', {}).get('resourceUri', 'Resource URI not found')
        operation_name = item.get('data', {}).get('operationName', 'Operation Name not found')
        status = item.get('data', {}).get('status', 'Status not found')
        subscription_id = item.get('data', {}).get('subscriptionId', 'Subscription ID not found')
        tenant_id = item.get('data', {}).get('tenantId', 'Tenant ID not found')
        event_time = item.get('eventTime', 'Event Time not found')

        print("======================================================")
        print("======================================================")
        print("======================================================")
        
        print(f"Event Time: {event_time}")
        print(f"Resource Provider: {resource_provider}")
        print(f"Resource ID: {resource_uri}")
        print(f"Operation Name: {operation_name}")
        print(f"Status: {status}")
        print(f"Subscription ID: {subscription_id}")
        print(f"Tenant ID: {tenant_id}")

        # 异步调用同步的 ResourceManagementClient
        resource = await asyncio.to_thread(get_resource, sync_credential, subscription_id, operation_name, resource_uri)
 
        print(f"Resource: {resource}")

    # 异步更新检查点
    await partition_context.update_checkpoint(event)


#Get Resource by Resource URL
def get_resource(credential, subscription_id, operation_name, resource_id):

    if "Microsoft.Compute/virtualMachines" in operation_name:
        #如果是虚拟机
        get_vm(credential, subscription_id, resource_id)



# 处理虚拟机资源
def get_vm(credential, subscription_id, resource_id):
    print("******************************************************")
    print("******************************************************")
    print("Get the Virtual Machine")
 
    resource_parts = resource_id.split('/')
    resource_group = resource_parts[4]
    vm_name = resource_parts[8]

    compute_client = ComputeManagementClient(credential, subscription_id)
    vm = compute_client.virtual_machines.get(resource_group, vm_name)
    print(f"VM Name: {vm.name}")
    print(f"VM Location: {vm.location}")
    print(f"VM Size: {vm.hardware_profile.vm_size}")
    print(f"VM Availability Zone: {vm.zones}")

    vm_instance_view = compute_client.virtual_machines.instance_view(resource_group, vm_name)
    # 虚拟机运行状态
    print(f"VM Status: {vm_instance_view.statuses[1].display_status}")


def on_partition_initialize(partition_context):
    print("Partition: {} has been initialized.".format(partition_context.partition_id))

def on_partition_close(partition_context, reason):
    print("Partition: {} has been closed, reason for closing: {}.".format(partition_context.partition_id, reason))

def on_error(partition_context, error):
    if partition_context:
        print(
            "An exception: {} occurred during receiving from Partition: {}.".format(
                partition_context.partition_id, error
            )
        )
    else:
        print("An exception: {} occurred during the load balance process.".format(error))

async def main():
    # 创建 BlobCheckpointStore 使用服务主体进行身份验证
    checkpoint_store = BlobCheckpointStore(
        blob_account_url=blob_storage_account_url,
        container_name=blob_container_name,
        credential=async_credential
    )

    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=eventhub_namespace,
        eventhub_name=eventhub_name,
        credential=async_credential,
        consumer_group=consumer_group,
        checkpoint_store=checkpoint_store,
    )

    async with consumer_client:
        await consumer_client.receive(
            on_event=on_event,
            on_partition_initialize=on_partition_initialize,
            on_partition_close=on_partition_close,
            on_error=on_error,
            starting_position="-1",  # "-1" 表示从最新的检查点开始
        )

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        print("Stopped receiving.")
    finally:
        loop.close()
