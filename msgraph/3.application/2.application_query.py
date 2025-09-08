import os
import asyncio
#pip3 install msgraph-sdk
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.applications.applications_request_builder import ApplicationsRequestBuilder


async def main():
    tenantid = os.environ.get('msdn_tenantid')
    clientid = os.environ.get('msdn_clientid')
    clientsecret = os.environ.get('msdn_clientsecret')

    #Graph API
    # Create a credential object. Used to authenticate requests
    ### https://github.com/microsoftgraph/msgraph-sdk-python/blob/main/docs/users_samples.md
    # Create a credential object. Used to authenticate requests
    credential = ClientSecretCredential(tenantid,clientid,clientsecret)
    scopes = ['https://graph.microsoft.com/.default']
    graph_service_client = GraphServiceClient(credentials=credential, scopes=scopes)

    #List All Application
    '''
    参考: https://learn.microsoft.com/en-us/graph/api/application-list?view=graph-rest-1.0&tabs=http
    检查Permissions
    '''

    # Get by Application id (Using Application Object ID)
    app  = await graph_service_client.applications.by_application_id("87d6b931-26ab-4b5b-b7d9-718a90978c4b").get()
    print(app.display_name, app.id)


if __name__ == "__main__":
    asyncio.run(main())
