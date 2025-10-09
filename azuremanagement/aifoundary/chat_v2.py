import os
import time
from datetime import datetime
from openai import AzureOpenAI

endpoint = "https://southeastasia-resource.cognitiveservices.azure.com/"
model_name = "gpt-4.1"
deployment = "gpt-4.1"

subscription_key = "[YourKey]]"
api_version = "2024-12-01-preview"

client = AzureOpenAI(
    api_version=api_version,
    azure_endpoint=endpoint,
    api_key=subscription_key,
)

for i in range(300):
    start_time = datetime.now()
    #print(f"Call {i+1} start time: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")

    response = client.chat.completions.create(
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant.",
            },
            {
                "role": "user",
                "content": "给我讲一个笑话",
            }
        ],
        max_completion_tokens=13107,
        temperature=1.0,
        top_p=1.0,
        frequency_penalty=0.0,
        presence_penalty=0.0,
        model=deployment
    )

    end_time = datetime.now()
    #print(f"Response: {response.choices[0].message.content}")
    #print(f"Call {i+1} end time: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Call {i+1} duration: {(end_time - start_time).total_seconds()} seconds")
    print("-" * 40)

    time.sleep(1)  # 间隔1秒
