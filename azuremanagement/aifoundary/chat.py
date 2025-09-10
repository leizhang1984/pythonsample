import requests
import json
import time

# 设置服务主体的环境变量
api_key = "[YourKey]"
endpoint = "https://southeastasia-resource.cognitiveservices.azure.com/openai/deployments/gpt-4.1/chat/completions?api-version=2025-01-01-preview"

# 请求头
headers = {
    "Content-Type": "application/json",
    "api-key": api_key
}

# 请求体
data = {
    "messages": [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": "请给我讲一个笑话"}
    ]
}

# 存储每次请求耗时的列表
elapsed_times = []

# 循环调用1000次
for i in range(1000):
    try:
        # 记录开始时间
        start_time = time.time()
        
        # 发送请求
        response = requests.post(endpoint, headers=headers, data=json.dumps(data))
        
        # 记录结束时间
        end_time = time.time()
        
        # 计算请求耗时
        elapsed_time = end_time - start_time
        elapsed_times.append(elapsed_time)
        
        # 检查响应状态码
        if response.status_code == 200:
            response_data = response.json()
            print(f"Response {i+1}:")
            # 打印响应中的内容
            completion_text = response_data['choices'][0]['message']['content']
            #print(completion_text)
        else:
            print(f"Request {i+1} failed with status code {response.status_code}")
            print(response.text)
        
        # 打印请求耗时
        print(f"Request {i+1} took {elapsed_time:.2f} seconds")
    
    except:
        print(f"Request {i+1} encountered an error:")
        elapsed_times.append(None)  # 用 None 表示失败的请求耗时

# 打印所有请求的耗时，只显示小数点后2位
formatted_elapsed_times = [f"{t:.2f}" if t is not None else "Error" for t in elapsed_times]
print("\nAll request durations (in seconds):")
print(formatted_elapsed_times)
