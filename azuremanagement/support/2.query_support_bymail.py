import os,pytz
from azure.identity import ClientSecretCredential, DefaultAzureCredential
from azure.mgmt.support import MicrosoftSupport
from azure.mgmt.resource import SubscriptionClient

'''
按照开工单人的联系邮箱，来检索开了多少工单
'''
def main():
    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    #需要查询的邮箱地址
    search_email_address = "leizha@microsoft.com"
    
    #显示北京时间
    target_timezone = pytz.timezone('Asia/Shanghai')

    #订阅名称
    #subscription_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"  
    
    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    subscription_client = SubscriptionClient(clientcredential)

    #循环所有的订阅
    for subscription in subscription_client.subscriptions.list():
        # 创建支持管理客户端
        support_client = MicrosoftSupport(clientcredential, subscription.subscription_id)

        #查询支持工单
        support_tickets = support_client.support_tickets.list()

        for ticket in support_tickets:
            #b遍历每一个工单
            primary_email_address = ticket.contact_details.primary_email_address

            #如果联系人邮箱相同
            if primary_email_address == search_email_address:

                #默认是UTC时区，转换一下时区
                ticket_created_date_chinatime = ticket.created_date.astimezone(target_timezone)

                #工单的：标题，描述，紧急程度，状态
                print(f"Ticket id: {ticket.support_ticket_id}, create time: {ticket_created_date_chinatime.strftime("%Y-%m-%d %H:%M:%S")}, title: {ticket.title}, severity: {ticket.severity}, status: {ticket.status}")
                #print(f"Ticket id: {ticket.support_ticket_id}, title: {ticket.title}, description: {ticket.description}, severity: {ticket.severity}, status: {ticket.status}")

                



if __name__ == "__main__":
    main()

