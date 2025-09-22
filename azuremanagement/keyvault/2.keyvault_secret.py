import os
from azure.identity import ClientSecretCredential
from azure.keyvault.secrets import SecretClient

def main():
    # 设置服务主体的环境变量
    tenant_id = os.environ.get('nonprod_tenantid')
    client_id = os.environ.get('nonprod_clientid')
    client_secret = os.environ.get('nonprod_clientsecret')


    # Key Vault 名称和 URL
    KEY_VAULT_NAME = "leilabkeyvault01"
    KEY_VAULT_URL = f"https://{KEY_VAULT_NAME}.vault.azure.net/"

    # 创建 ClientSecretCredential
    credential = ClientSecretCredential(tenant_id=tenant_id, client_id=client_id, client_secret=client_secret)

    # 创建 SecretClient
    secret_client = SecretClient(vault_url=KEY_VAULT_URL, credential=credential)

    # Secret 名称
    secret_name = "mysqlconnectionstring"
    secret_value = "server=192.1.1.1;uid=admin;pwd=your_password;database=your_db"
    # 设置secret
    secret_client.set_secret(secret_name,secret_value)


   # 获取所有版本的 secret
    print(f"All versions of the secret '{secret_name}':")
    secret_versions = secret_client.list_properties_of_secret_versions(secret_name)
    for version in secret_versions:
        versioned_secret = secret_client.get_secret(secret_name, version.version)
        print(f"Version: {version.version}, Value: {versioned_secret.value}")


if __name__ == "__main__":
    main()
