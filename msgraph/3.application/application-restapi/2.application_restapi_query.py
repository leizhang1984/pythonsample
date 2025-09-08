import os
import requests
#pip3 install msgraph-sdk
from azure.identity import ClientSecretCredential
from msgraph import GraphServiceClient
from msgraph.generated.applications.applications_request_builder import ApplicationsRequestBuilder


def main():
    tenantid = os.environ.get('msdn_tenantid')
    clientid = os.environ.get('msdn_clientid')
    clientsecret = os.environ.get('msdn_clientsecret')

    # 1.先获得Access Token
    token_endpoint = f'https://login.microsoftonline.com/{tenantid}/oauth2/v2.0/token'

    # Define the required parameters for the token endpoint
    data = {
        'client_id': clientid,
        'client_secret': clientsecret,
        'scope': 'https://graph.microsoft.com/.default',
        'grant_type': 'client_credentials'
    }
    # Make a request to the token endpoint to obtain an access token
    response = requests.post(token_endpoint, data=data)

    # 获得Access Token, Access Token的有效期为3600秒
    access_token = response.json()['access_token']
    # print(access_token)
    
    #Application List All
    url = f"https://graph.microsoft.com/v1.0/applications"

    headers = {'Authorization': f'Bearer {access_token}',
               'ConsistencyLevel': 'eventual'}

    response = requests.get(url, headers = headers)
    response_data = response.json()
    
        # 检查是否成功获取数据
    if 'value' in response_data:
        applications = response_data['value']
        for app in applications:
            app_id = app.get('id')
            app_display_name = app.get('displayName')
            print(f"Application: {app_display_name} (ID: {app_id})")

            # 获取密码凭据
            password_cred_url = f"https://graph.microsoft.com/v1.0/applications/{app_id}/passwordCredentials"
            password_cred_response = requests.get(password_cred_url, headers=headers)
            password_cred_data = password_cred_response.json()

            if 'value' in password_cred_data:
                password_credentials = password_cred_data['value']
                if password_credentials:
                    for cred in password_credentials:
                        displayname = cred.get('displayName')
                        hint = cred.get('hint')
                        start_date = cred.get('startDateTime')
                        end_date = cred.get('endDateTime')
                        print(f"  Password Display Name is {displayname}, hint is {hint}, valid date from {start_date} to {end_date}")
                else:
                    print("  No password credentials found.")
            else:
                print("  Failed to retrieve password credentials.")
    else:
        print("Failed to retrieve applications.")


if __name__ == "__main__":
    main()
