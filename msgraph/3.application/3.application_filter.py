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
   
    # Filter
    query_params = ApplicationsRequestBuilder.ApplicationsRequestBuilderGetQueryParameters(
		filter = "startswith(displayName, '20240726User')",
		count = True,
        #top = 10,
		orderby = ["displayName"],
        )

    request_configuration = ApplicationsRequestBuilder.ApplicationsRequestBuilderGetRequestConfiguration(
    query_parameters = query_params,
    )
    request_configuration.headers.add("ConsistencyLevel", "eventual")

    app = await graph_service_client.applications.get(request_configuration = request_configuration)
    print(app)

if __name__ == "__main__":
    asyncio.run(main())
