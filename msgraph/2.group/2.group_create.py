import os
import asyncio
#pip3 install msgraph-sdk
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.models.group import Group

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

    # Create Group
    '''
    参考: https://learn.microsoft.com/en-us/graph/api/group-post-groups?view=graph-rest-1.0&tabs=http
    检查Permissions
    '''
    request_body = Group(
        description = "DemoGroup01",
	    display_name = "DemoGroup01",
	    group_types = [],
        mail_enabled = False,
        mail_nickname = "DemoGroup01",
        security_enabled = True,
    )
    result = await graph_service_client.groups.post(request_body)
    print(result)


    

if __name__ == "__main__":
    asyncio.run(main())
