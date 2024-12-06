import os

from azure.core.exceptions import HttpResponseError
from azure.identity import ClientSecretCredential
from azure.mgmt.servicebus import ServiceBusManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.network import NetworkManagementClient


def main():

    tenantid = os.environ.get('msdn_tenantid')
    clientid = os.environ.get('msdn_clientid')
    clientsecret = os.environ.get('msdn_clientsecret')


    SUBSCRIPTION_ID = "b5aa1700-1510-4f35-b134-fe9c7c695df1"
    GROUP_NAME = "test-rg"
    NAMESPACE = "leiservicebus02"

    # Create client
    # # For other authentication approaches, please see: https://pypi.org/project/azure-identity/

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    servicebus_client = ServiceBusManagementClient(
        credential=clientcredential,
        subscription_id=SUBSCRIPTION_ID
    )

    # Create namespace
    namespace = servicebus_client.namespaces.begin_create_or_update(
        GROUP_NAME,
        NAMESPACE,
        {
          "sku": {
            "name": "Basic",
            "tier": "Basic"
          },
          "location": "japaneast",
          "tags": {
            "tag1": "value1",
            "tag2": "value2"
          }
        }
    ).result()
    print("Create namespace:\n{}".format(namespace))

    # Get namespace
    namespace = servicebus_client.namespaces.get(
        GROUP_NAME,
        NAMESPACE
    )
    print("Get namespace:\n{}".format(namespace))


if __name__ == "__main__":
    main()