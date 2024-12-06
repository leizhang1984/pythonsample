import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
#pip3 install azure-storage-blob
from azure.storage.blob import BlobServiceClient

#pip3 install azure-storage-blob

tenantid = os.environ.get('tenantid')
clientid = os.environ.get('clientid')
clientsecret = os.environ.get('clientsecret')


def main():
    SUBSCRIPTION_ID = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    GROUP_NAME = "test-rg"
    STORAGE_ACCOUNT = "leiteststorage002"
    location = "germanywestcentral"
    container_name = "privatecontainer02"

    local_filepath = "D:\Work\picture"
    local_file_name = "azurelogo.jpg"

    account_url = "https://" + STORAGE_ACCOUNT + ".blob.core.windows.net"

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    # Create the BlobServiceClient object
    # 把自己的账户加权限： Storage Blob Data Contributor 
    blob_service_client = BlobServiceClient(account_url, credential = clientcredential)

    #使用本地文件
    upload_file_path = os.path.join(local_filepath, local_file_name)

    # Create a blob client using the local file name as the name for the blob
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=local_file_name)

    print("\nUploading to Azure Storage as blob:\n\t" + local_file_name)

    # Upload the created file
    with open(file=upload_file_path, mode="rb") as data:
        blob_client.upload_blob(data)


if __name__ == '__main__':
    main()
