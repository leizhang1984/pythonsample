
import os
import time

from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.support import MicrosoftSupport
from azure.mgmt.support.models import ContactProfile, SupportTicketDetails, Service, ProblemClassification, UpdateSupportTicket

'''
创建支持工单
'''
def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    #订阅名称
    subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"   
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

    # 创建支持管理客户端
    support_client = MicrosoftSupport(clientcredential, subscription_id)

    #标题
    title = "Azure VM Issue"
    #描述
    description = "This is a sample support ticket created via Python SDK."

     #严重性级别，CRITICAL，HIGHESTCRITICALIMPACT，MINIMAL，MODERATE
     #注意如果是中文支持的话，python code创建的时候严重性只能是最低minimal
    severity = "moderate" #minimal
    #是否需要24*7
    require24_x7_response = False
    #高级诊断设置
    advanced_diagnostic_consent="Yes"
    
    # 定义支持工单的详细信息
    support_ticket_details = SupportTicketDetails(
        #标题
        title = title,
        #描述
        description = description,
        #严重性级别
        severity = severity,
        #是否需要24*7
        require24_x7_response = require24_x7_response,
        advanced_diagnostic_consent = advanced_diagnostic_consent,

        #这里的Service ID是Virtual Machine running Linux"
        service_id = "/providers/Microsoft.Support/services/cddd3eb5-1830-b494-44fd-782f691479dc",

        problem_classification_id = "/providers/Microsoft.Support/services/cddd3eb5-1830-b494-44fd-782f691479dc/problemClassifications/46d3b5cb-4fa8-12e0-c525-9c41d42dcb8b",
        #'problem_classification_display_name': 'VM Performance / Disk throughput or IOPS are lower than expected'

        #is_temporary_ticket = "Yes",

        contact_details = ContactProfile(
            first_name ="Lei",
            last_name = "Zhang",

            preferred_contact_method = "email",
            primary_email_address = "leizha@microsoft.com",

            #phone_number = "+86 ",
            preferred_time_zone = "China Standard Time",

            country = "CHN",
            preferred_support_language = "zh-hans"
        )
    )

    #注意Ticket Name名字要唯一
    ticket_name = "sample_support_ticket_0"

    #创建支持工单,
    support_ticket = support_client.support_tickets.begin_create(
        support_ticket_name = ticket_name,
        create_support_ticket_parameters = support_ticket_details).result()


    print(f"Created support ticket: {support_ticket.support_ticket_id}")


if __name__ == "__main__":
    main()

'''
    List Service:
    https://learn.microsoft.com/en-us/rest/api/support/services/list?view=rest-support-2024-04-01&tabs=HTTP

      "id": "/providers/Microsoft.Support/services/cddd3eb5-1830-b494-44fd-782f691479dc",
      "name": "cddd3eb5-1830-b494-44fd-782f691479dc",
      "type": "Microsoft.Support/services",
      "properties": {
        "displayName": "Virtual Machine running Linux",
        "resourceTypes": [
          "MICROSOFT.CLASSICCOMPUTE/VIRTUALMACHINES",
          "MICROSOFT.COMPUTE/VIRTUALMACHINES"
        ]
      }
'''

'''

'''