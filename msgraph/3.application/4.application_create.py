import os
import asyncio

from azure.identity import ClientSecretCredential
#pip3 install msgraph-sdk
from msgraph import GraphServiceClient
from msgraph.generated.models.application import Application
from msgraph.generated.applications.item.add_password.add_password_post_request_body import AddPasswordPostRequestBody
from msgraph.generated.models.password_credential import PasswordCredential

from msgraph.generated.models.service_principal import ServicePrincipal


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

    # Create Application
    '''
    参考: https://learn.microsoft.com/en-us/graph/api/application-post-applications?view=graph-rest-1.0&tabs=python
    检查Permission
    '''

    # Create Application
    request_body = Application(
        display_name = "20240409-Application",
    )

    newapplication = await graph_service_client.applications.post(request_body)
    new_app_id = newapplication.app_id
    new_obj_id = newapplication.id
    print(newapplication)

    # Add Password
    # 设置密码过期时间为100年
    # 注意需要修改：App Management Policy，
    # https://www.cnblogs.com/threestone/p/18080874
    request_body = AddPasswordPostRequestBody(
	password_credential = PasswordCredential(
		display_name = "Password100Years",
        start_date_time = "2024-04-10T00:00:00.0000000Z",
        end_date_time = "2123-10-20T00:00:00.0000000Z"
	    ),
    )

    # 使用上面新建的ID
    result = await graph_service_client.applications.by_application_id(new_obj_id).add_password.post(request_body)

    ########################################################################################
    ########################################################################################
    ########################################################################################
    # Create Service Principle
    request_body = ServicePrincipal(
	app_id = new_app_id
    )

    result = await graph_service_client.service_principals.post(request_body)
    print(result)


if __name__ == "__main__":
    asyncio.run(main())
