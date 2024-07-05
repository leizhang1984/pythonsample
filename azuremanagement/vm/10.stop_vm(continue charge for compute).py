import os
from azure.identity import DefaultAzureCredential,ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient

tenantid = os.environ.get('nonprod_tenantid')
clientid = os.environ.get('nonprod_clientid')
clientsecret = os.environ.get('nonprod_clientsecret')

def main():
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    compute_client = ComputeManagementClient(
        credential = clientcredential,
        subscription_id = subscription_id
    )


    vm = compute_client.virtual_machines.begin_power_off("lab-rg", "privatevm2019").result()
    print("Stop virtual machine. Please note this vm will continue charge for compute")
    print(vm)


if __name__ == '__main__':
    main()