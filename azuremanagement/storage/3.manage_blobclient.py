import os
import mimetypes
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.storage.blob import BlobServiceClient,generate_blob_sas,BlobSasPermissions,ContentSettings
from azure.core.exceptions import ResourceExistsError
from datetime import datetime, timedelta
from azure.mgmt.storage import StorageManagementClient
#pip3 install azure-storage-blob

tenantid = os.environ.get('nonprod_tenantid')
clientid = os.environ.get('nonprod_clientid')
clientsecret = os.environ.get('nonprod_clientsecret')


def main():
    #订阅名称
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    #资源组名称
    resourcegroup_name = "test-rg"
    #存储账户名称
    storage_account_name = "leiteststorage000"
    #Azure存储账户所在数据中心区域，germanywestcentral就是Azure德国法兰克福
    location = "germanywestcentral"
    #容器名称，默认是不允许匿名访问
    container_name = "privatecontainer"

    #本地文件夹路径
    local_filepath = "D:\Work\picture"
    #本地文件名称
    #local_file_name = "azurelogo.jpg"
    local_file_name = "1.txt"
    #云端的文件名，默认和本地保持一致
    blob_name = local_file_name

    account_url = "https://" + storage_account_name + ".blob.core.windows.net"

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    storage_client = StorageManagementClient(clientcredential,subscription_id)

    # Create the BlobServiceClient object
    # 把自己的账户加权限： Storage Blob Data Contributor 
    blob_service_client = BlobServiceClient(account_url, credential = clientcredential)

    # 获取 ContainerClient
    container_client = blob_service_client.get_container_client(container_name)

    # 检查容器是否存在，如果不存在则创建它
    try:
        container_client.create_container()
        print(f"Container '{container_name}' created.")
    except ResourceExistsError:
        print(f"Container '{container_name}' already exists.")


    #使用本地文件
    upload_file_path = os.path.join(local_filepath, local_file_name)

    # 根据文件扩展名自动设置 Content-Type
    content_type, _ = mimetypes.guess_type(upload_file_path)
    if content_type is None:
        content_type = "application/octet-stream"  # 默认的 Content-Type
    content_settings = ContentSettings(content_type=content_type)

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

    print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)


    # Upload the created file
    with open(file=upload_file_path, mode="rb") as data:
        #overwrite=True 表示如果云上存在同样文件名，默认覆盖
        blob_client.upload_blob(data,overwrite=True,content_settings=content_settings)
    
    # 获取用户委托密钥
    user_delegation_key = blob_service_client.get_user_delegation_key(
        key_start_time=datetime.utcnow(),
        key_expiry_time=datetime.utcnow() + timedelta(hours=1)
    )
    #上传完毕后，下载
    sas_token = generate_blob_sas(
        account_name=storage_account_name,
        container_name=container_name,
        blob_name=blob_name,
        user_delegation_key=user_delegation_key,
        #默认的权限是Read，读操作
        permission=BlobSasPermissions(read=True),
        #访问的开始时间是当前时间，
        #访问的结束时间是后面1小时内
        expiry=datetime.utcnow() + timedelta(hours=1)  # 设置 SAS 令牌的过期时间
    )


    # 生成带有 SAS 令牌的下载链接
    blob_url_with_sas = f"https://{storage_account_name}.blob.core.windows.net/{container_name}/{blob_name}?{sas_token}"
    
    print("\nAzure Blob下载链接是：\n\t" + blob_url_with_sas)

if __name__ == '__main__':
    main()
