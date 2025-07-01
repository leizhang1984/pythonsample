import os
from datetime import datetime
from azure.identity import ClientSecretCredential
from azure.storage.blob import BlobServiceClient

def main():
    # 替换为你的 Azure AD 租户 ID、客户端 ID 和客户端密钥
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    # 替换为你的存储账户名称和容器名称
    storage_account_name = "leizhangcostmanagement01"
    container_name = 'report'

     # 本地下载目录
    download_directory = 'D:\\'  # 确保使用双反斜杠

    # 创建服务主体认证凭据
    credential = ClientSecretCredential(tenantid, clientid, clientsecret)

    # 创建 BlobServiceClient
    blob_service_client = BlobServiceClient(account_url=f"https://{storage_account_name}.blob.core.windows.net", credential=credential)

    # 获取容器客户端
    container_client = blob_service_client.get_container_client(container_name)

    # 目标日期
    target_date = datetime(2025, 6, 30)

   
    # 列出容器中的所有 blob
    blobs = container_client.list_blobs()

    for blob in blobs:
        # 检查文件名是否包含 "daily-actual-cost" 且扩展名为 ".csv"
        # daily-actual-cost表示的是实际费用
        if "daily-actual-cost" in blob.name and blob.name.lower().endswith('.csv'):
            # 获取 blob 的属性
            blob_client = container_client.get_blob_client(blob)
            properties = blob_client.get_blob_properties()
            
            # 检查创建日期
            if properties.creation_time.date() == target_date.date():
                # 下载 blob 到本地文件
                download_file_path = os.path.join(download_directory, blob.name)
                os.makedirs(os.path.dirname(download_file_path), exist_ok=True)
                
                with open(download_file_path, "wb") as download_file:
                    download_file.write(blob_client.download_blob().readall())
                
                print(f"Downloaded {blob.name} to {download_file_path}")

if __name__ == "__main__":
    main()
