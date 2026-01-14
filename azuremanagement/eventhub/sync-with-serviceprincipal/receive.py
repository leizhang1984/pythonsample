import os
import json
import asyncio
from azure.eventhub.aio import EventHubConsumerClient
from azure.eventhub.extensions.checkpointstoreblobaio import BlobCheckpointStore
from azure.identity.aio import ClientSecretCredential

# Event Hub 配置
eventhub_namespace = "azuremonitorns.servicebus.windows.net"  # os.getenv("EVENT_HUB_NAMESPACE")
eventhub_name = "administrative"  # os.getenv("EVENT_HUB_NAME")
consumer_group = "pythonclient"  # 需要提前创建好：consumer_group

# Blob 存储配置
blob_storage_account_url = 'azuremonitorns01.blob.core.windows.net'  #os.getenv('BLOB_STORAGE_ACCOUNT_URL')
blob_container_name = 'administrative' #os.getenv('BLOB_CONTAINER_NAME')

# 服务主体（Service Principal）配置
tenantid = os.environ.get('nonprod_tenantid')
clientid = os.environ.get('nonprod_clientid')
clientsecret = os.environ.get('nonprod_clientsecret')

# 创建 ClientSecretCredential
credential = ClientSecretCredential(tenantid, clientid, clientsecret)

async def on_event(partition_context, event):
    print("======================================================")
    print("======================================================")
    print("======================================================")
    print("Received event from partition: {}.".format(partition_context.partition_id))
    print(f"Data: {event.body_as_str()}")
    # 将事件数据保存为JSON文件
    event_data = {
        "partition_id": partition_context.partition_id,
        "sequence_number": event.sequence_number,
        "offset": event.offset,
        "enqueued_time": event.enqueued_time.isoformat(),
        "body": event.body_as_str()
    }
    # 异步更新检查点
    await partition_context.update_checkpoint(event)

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
        credential=credential
    )

    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=eventhub_namespace,
        eventhub_name=eventhub_name,
        credential=credential,
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
