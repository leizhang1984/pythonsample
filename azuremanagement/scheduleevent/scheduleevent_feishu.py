import json
import requests
from datetime import datetime

metadata_url = "http://169.254.169.254/metadata/scheduledevents"
header = {'Metadata': 'true'}
query_params = {'api-version': '2020-07-01'}
feishu_webhook_url = "https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxxxxxxxxxx"  # 替换为你的飞书 Webhook URL

def get_scheduled_events():
    resp = requests.get(metadata_url, headers=header, params=query_params)
    data = resp.json()
    return data

def send_to_feishu(event_data):
    message = {
        "msg_type": "text",
        "content": {
            "text": f"Azure Scheduled Event: {json.dumps(event_data, indent=2)}"
        }
    }
    headers = {'Content-Type': 'application/json'}
    response = requests.post(feishu_webhook_url, headers=headers, data=json.dumps(message))
    if response.status_code == 200:
        log_message("Message sent successfully to Feishu bot!")
    else:
        log_message(f"Failed to send message. Status code: {response.status_code}, Response: {response.text}")

def log_message(message):
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"{current_time} - {message}")

def main():
    events = get_scheduled_events()
    if events.get("Events"):
        send_to_feishu(events)
    #else:
        #log_message("No event to send.")

if __name__ == "__main__":
    main()


# [root@prometheus01 ~]# crontab -l
# * * * * * /usr/bin/python3 /root/scheduleevent-feishu.py >> /root/schedule-feishu.log 2>&1
