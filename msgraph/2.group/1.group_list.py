import os
import asyncio
#pip3 install msgraph-sdk
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.groups.groups_request_builder import GroupsRequestBuilder

tenantid = os.environ.get('tenantid')
clientid = os.environ.get('clientid')
clientsecret = os.environ.get('clientsecret')

async def main():
  
    #Graph API
    # Create a credential object. Used to authenticate requests
    ### https://github.com/microsoftgraph/msgraph-sdk-python/blob/main/docs/users_samples.md
    # Create a credential object. Used to authenticate requests
    credential = ClientSecretCredential(tenantid,clientid,clientsecret)
    scopes = ['https://graph.microsoft.com/.default']
    graph_service_client = GraphServiceClient(credentials=credential, scopes=scopes)

    # List All Group
    '''
    参考: https://learn.microsoft.com/en-us/graph/api/group-list?view=graph-rest-1.0&tabs=http
    检查Permissions
    '''
    
    # List All Group
    groups = await graph_service_client.groups.get()
    print(groups)

    # Get by group id
    group  = await graph_service_client.groups.by_group_id("22fd1119-5f07-4e98-86b2-6da94be0aeea").get()
    print(group.display_name, group.id)
    #print(user.user_principal_name, user.display_name, user.id)

    #Use Filter
    query_params = GroupsRequestBuilder.GroupsRequestBuilderGetQueryParameters(
		filter = "startswith(displayName, 'M')",
		count = True,
		#top = 10,
		orderby = ["displayName"],
    )
    
    request_configuration = GroupsRequestBuilder.GroupsRequestBuilderGetRequestConfiguration(
        query_parameters = query_params,
    )
    request_configuration.headers.add("ConsistencyLevel", "eventual")

    result = await graph_service_client.groups.get(request_configuration = request_configuration)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
