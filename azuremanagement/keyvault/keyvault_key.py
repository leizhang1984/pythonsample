import os
from azure.identity import ClientSecretCredential
from azure.keyvault.keys import KeyClient
from azure.keyvault.keys.crypto import CryptographyClient, EncryptionAlgorithm


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

    # 创建 KeyClient
    key_client = KeyClient(vault_url=KEY_VAULT_URL, credential=credential)

    # 密钥名称
    key_name = "key01"

    # 列出密钥的所有版本
    versions = key_client.list_properties_of_key_versions(key_name)
    version_ids = [version.id for version in versions]
    print("Available key versions:")
    for version_id in version_ids:
        print(version_id)

    # 选择一个特定版本（这里选择第一个版本）
    key_version = version_ids[0] if version_ids else None
    if key_version is None:
        print("No key versions found.")
        return

    # 获取指定版本的密钥
    key = key_client.get_key(key_name, key_version.split('/')[-1])

    # 创建 CryptographyClient
    crypto_client = CryptographyClient(key, credential=credential)

    # 要加密的字符串
    plaintext = "YourMySQLConnectionString"

    # 加密字符串
    encrypt_result = crypto_client.encrypt(EncryptionAlgorithm.rsa_oaep, plaintext.encode())
    encrypted_data = encrypt_result.ciphertext

    print(f"Encrypted data: {encrypted_data.hex()}")

    # 解密字符串
    decrypt_result = crypto_client.decrypt(EncryptionAlgorithm.rsa_oaep, encrypted_data)
    decrypted_data = decrypt_result.plaintext.decode()

    print(f"Decrypted data: {decrypted_data}")

if __name__ == "__main__":
    main()
