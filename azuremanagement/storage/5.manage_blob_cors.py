
import os

from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.storage import StorageManagementClient
from azure.mgmt.resource import ResourceManagementClient

from azure.storage.blob import BlobAnalyticsLogging, Metrics, CorsRule, RetentionPolicy
from azure.storage.blob import BlobServiceClient


def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    SUBSCRIPTION_ID = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    GROUP_NAME = "test-rg"
    STORAGE_ACCOUNT = "leiteststorage001"
    location = "germanywestcentral"

    account_url = "https://" + STORAGE_ACCOUNT + ".blob.core.windows.net"

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    blob_service_client = BlobServiceClient(account_url, credential=clientcredential)
    
    # Create CORS rules
    cors_rule = CorsRule(['www.xyz.com'], ['GET'])
    cors = [cors_rule]

    blob_service_client.set_service_properties(None,None,None,cors)


if __name__ == "__main__":
    main()