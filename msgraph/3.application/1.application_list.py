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
    # 列出所有的application
    apps_response = await graph_service_client.applications.get()
    apps = apps_response.value

    # 循环所有的applications
    for app in apps:
        app_id = app.app_id
        app_display_name = app.display_name
        print(f"Checking Application: {app_display_name} (ID: {app_id})")
   
        one_app = graph_service_client.applications.by_application_id(app_id).get()
        print(one_app)



if __name__ == "__main__":
    asyncio.run(main())
