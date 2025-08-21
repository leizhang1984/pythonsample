import json
import requests
from azure.eventhub import EventHubProducerClient, EventData

# Azure Scheduled Events metadata URL and headers
metadata_url = "http://169.254.169.254/metadata/scheduledevents"
header = {'Metadata': 'true'}
query_params = {'api-version': '2020-07-01'}

# Azure Event Hub connection details
event_hub_connection_str = 'Endpoint=sb://leischeduleeventns.servicebus.windows.net/;SharedAccessKeyName=RootManageSharedAccessKey;SharedAccessKey=XXXXXXXXXXXXXXXXXXXXXXXX'
event_hub_name = 'scheduleevent'

def get_scheduled_events():
    """Fetch scheduled events from Azure metadata service."""
    resp = requests.get(metadata_url, headers=header, params=query_params)
    data = resp.json()
    return data

def send_events_to_event_hub(events):
    """Send events to Azure Event Hub."""
    producer = EventHubProducerClient.from_connection_string(
        conn_str=event_hub_connection_str,
        eventhub_name=event_hub_name
    )
    
    # Create a batch.
    event_data_batch = producer.create_batch()

    for event in events.get('Events', []):
        event_data = EventData(json.dumps(event))
        event_data_batch.add(event_data)
    
    # Send the batch of events to the event hub.
    producer.send_batch(event_data_batch)
    producer.close()
    
def main():
    scheduled_events = get_scheduled_events()
    if 'Events' in scheduled_events and scheduled_events['Events']:
        send_events_to_event_hub(scheduled_events)
    else:
        print("No scheduled events found.")

if __name__ == "__main__":
    main()

