"""
An example to show receiving events from an Event Hub.
"""
import os
from azure.core.credentials import AzureNamedKeyCredential
from azure.eventhub import EventHubConsumerClient
from azure.identity import ClientSecretCredential

#需要把下面的Service Principal权限设置为：Azure Event Hubs Data Receiver
tenantid = os.environ.get('nonprod_tenantid')
clientid = os.environ.get('nonprod_clientid')
clientsecret = os.environ.get('nonprod_clientsecret')

eventhub_namespace = "azuremonitorns.servicebus.windows.net"  #os.getenv("EVENT_HUB_NAMESPACE")
eventhub_name = "resourcehealth" #os.getenv("EVENT_HUB_NAME")

#需要提前设置consumer_group
consumer_group = "demo"

def on_event(partition_context, event):
    # Put your code here.
    # If the operation is i/o intensive, multi-thread will have better performance.
    print("Received event from partition: {}.".format(partition_context.partition_id))
    print(f"Data: {event.body_as_str()}")
    #partition_context.update_checkpoint(event)


def on_partition_initialize(partition_context):
    # Put your code here.
    print("Partition: {} has been initialized.".format(partition_context.partition_id))


def on_partition_close(partition_context, reason):
    # Put your code here.
    print("Partition: {} has been closed, reason for closing: {}.".format(partition_context.partition_id, reason))


def on_error(partition_context, error):
    # Put your code here. partition_context can be None in the on_error callback.
    if partition_context:
        print(
            "An exception: {} occurred during receiving from Partition: {}.".format(
                partition_context.partition_id, error
            )
        )
    else:
        print("An exception: {} occurred during the load balance process.".format(error))


if __name__ == "__main__":

   # 使用服务主体进行身份验证
    credential = ClientSecretCredential(tenantid, clientid, clientsecret)

    consumer_client = EventHubConsumerClient(
        fully_qualified_namespace=eventhub_namespace,
        eventhub_name=eventhub_name,
        credential=credential,
        consumer_group=consumer_group,
    )

    try:
        with consumer_client:
            consumer_client.receive(
                on_event=on_event,
                on_partition_initialize=on_partition_initialize,
                on_partition_close=on_partition_close,
                on_error=on_error,
                starting_position="-1",  # "-1" is from the beginning of the partition.
            )
    except KeyboardInterrupt:
        print("Stopped receiving.")