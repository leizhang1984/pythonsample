import os
from azure.identity import ClientSecretCredential
from azure.mgmt.billingbenefits import BillingBenefitsRP

# 查询节约计划
def main():
    # 替换为你的 Service Principal 信息
    tenant_id = os.getenv('msdn_tenantid')
    client_id = os.getenv('msdn_clientid')
    client_secret = os.getenv('msdn_clientsecret')

    # 使用 Service Principal 进行认证
    client_credential = ClientSecretCredential(tenant_id, client_id, client_secret)

    # 创建消费管理客户端
    client = BillingBenefitsRP(client_credential)

    response = client.savings_plan.list_all()
    for item in response:
        print(item)

if __name__ == "__main__":
    main()
