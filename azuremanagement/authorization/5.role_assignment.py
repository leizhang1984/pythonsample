
import os
import uuid

from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.authorization import AuthorizationManagementClient
from azure.mgmt.resource import ResourceManagementClient

tenantid = os.environ.get('tenantid')
clientid = os.environ.get('clientid')
clientsecret = os.environ.get('clientsecret')

#订阅ID
subscriptionid = "b5aa1700-1510-4f35-b134-fe9c7c695df1"
#资源组名称
resourcegroupname = "test-rg"

'''
https://github.com/Azure-Samples/azure-samples-python-management/blob/main/samples/authorization/manage_role_assignment.py
'''

def main():
    roleassignment = uuid.uuid4()
    
    #role definition参考：https://learn.microsoft.com/en-us/azure/role-based-access-control/built-in-roles
    reader_role_definition = "acdd72a7-3385-48ef-bd42-f606fba81ae7" #"2a2b9908-6ea1-4ae2-8e65-a410df84e7d1
    storageblobdatacontributor_role_definition = "ba92f5b4-2d11-453d-a403-e96b0029c9fe" #ba92f5b4-2d11-453d-a403-e96b0029c9fe"

    #2.需要分配的对象，这里我使用资源组
    scope = "subscriptions/{subscriptionId}/resourcegroups/{resourceGroupName}".format(
        subscriptionId = subscriptionid,
        resourceGroupName = resourcegroupname
    )    

    credential = ClientSecretCredential(tenantid,clientid,clientsecret)

    authorization_client = AuthorizationManagementClient(
        credential=credential,
        subscription_id=subscriptionid
    )
    #3.拿到Service Principle的Object ID
    assigned_sp_objectID = "a576132e-4aa5-4263-8ff6-9f853720c366"


    #第一次分配权限，Reader
    #https://learn.microsoft.com/en-us/python/api/azure-mgmt-authorization/azure.mgmt.authorization.v2022_04_01.models.roleassignmentcreateparameters?view=azure-python
    role_assignment = authorization_client.role_assignments.create(
        scope,
        roleassignment,
        {
          "role_definition_id": "/subscriptions/" + subscriptionid + "/providers/Microsoft.Authorization/roleDefinitions/" + reader_role_definition,
          "principal_id": assigned_sp_objectID,
          "description": "1st role assignment"
        }
    )
    print("Create 1st role assignment:\n{}".format(role_assignment))


    #第二次分配权限，Storage Blob Data Contributor
    #if 2nd roleassignment is same as 1st action, then update RBAC
    #if 2nd roleassignment is a new GUID, then create a new Role Assignment
    #roleassignment = uuid.uuid4()
    
    role_assignment = authorization_client.role_assignments.create(
        scope,
        roleassignment,
        {
          "role_definition_id": "/subscriptions/" + subscriptionid + "/providers/Microsoft.Authorization/roleDefinitions/" + storageblobdatacontributor_role_definition,
          "principal_id": assigned_sp_objectID,
          "description": "2nd role assignment"
        }
    )
    print("Create 2nd role assignment:\n{}".format(role_assignment))

if __name__ == "__main__":
    main() 