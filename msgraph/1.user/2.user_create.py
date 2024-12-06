import os
import asyncio

from azure.identity import ClientSecretCredential
#pip3 install msgraph-sdk
from msgraph import GraphServiceClient
from msgraph.generated.models.user import User
from msgraph.generated.models.password_profile import PasswordProfile


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
    graph_service_client  = GraphServiceClient(credentials=credential, scopes=scopes)

    # Create User
    '''
    参考: https://learn.microsoft.com/en-us/graph/api/user-post-users?view=graph-rest-1.0&tabs=python#response
    检查Permission
    '''

    # New User Property
    request_body = User(
        account_enabled = True,
        display_name = "user88",
        mail_nickname = "user88",
        user_principal_name = "user88@leiwaad.onmicrosoft.com",
        password_profile = PasswordProfile(
            force_change_password_next_sign_in = True,
            password = "xWwvJ]6NMw+bWH-d",
        ),
    )

    newuser = await graph_service_client.users.post(request_body)
    print(newuser)


if __name__ == "__main__":
    asyncio.run(main())
