import os
import asyncio
#pip3 install msgraph-sdk
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.users.users_request_builder import UsersRequestBuilder


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

    #List All User
    '''
    参考: https://learn.microsoft.com/en-us/graph/api/user-list?view=graph-rest-1.0&tabs=http
    检查Permissions
    '''
    # List All Users
    users = await graph_service_client.users.get()
    print(users)

    # List by user id
    user  = await graph_service_client.users.by_user_id("user01@leiwaad.onmicrosoft.com").get()
    print(user.user_principal_name, user.display_name, user.id)

    # Filter by display name
    query_params = UsersRequestBuilder.UsersRequestBuilderGetQueryParameters(
		filter = "startswith(displayName,'u')",
		orderby = ["userPrincipalName"],
		count = True,
        )
    request_configuration = UsersRequestBuilder.UsersRequestBuilderGetRequestConfiguration(
    query_parameters = query_params,
    )
    request_configuration.headers.add("ConsistencyLevel", "eventual")

    result = await graph_service_client.users.get(request_configuration = request_configuration)
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
