'''
从镜像仓库创建虚拟机的脚本
创建的时候会在网卡上绑定安全组
'''
import os,time,sys,asyncio

from azure.identity import DefaultAzureCredential,ClientSecretCredential,CertificateCredential
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.compute.models import (HardwareProfile, OSProfile, StorageProfile,
                                       ImageReference, NetworkProfile, NetworkInterfaceReference,
                                       VirtualMachine, SshConfiguration, SshPublicKey)
from azure.core.exceptions import ResourceNotFoundError
from concurrent.futures import ThreadPoolExecutor,as_completed

def create_vm(n):

    tenantid = os.environ.get('nonprod_tenantid')
    clientid = os.environ.get('nonprod_clientid')
    clientsecret = os.environ.get('nonprod_clientsecret')

    #Azure数据中心
    location = "germanywestcentral"
    #订阅ID
    sub_id = "166157a8-9ce9-400b-91c7-1d42482b83d6"
    #资源组
    rg_name = "jtvmss-rg"
    #virtual network name
    vnet_name = "jt-vnet"
    #子网
    subnet_name = "vm-subnet"

    #之前提前创建好vmss，类型必须是Flexible，Initial instance count必须为0
    vmss_name = "jtvmss-zone123"

    #创建的虚拟机名称
    vm_name = f"jtvmss-group2-{n}"
    #计算机名称
    computer_name = vm_name
    #网卡名称
    nic_name = vm_name + "-nic"

    vm_size = "Standard_D2s_v5" #dlsv5, esv5

    
    # 虚拟机可用区，1, 2, 3 轮流使用
    # 也可以直接设置为 1， 或者2，或者3
    availability_zone = str((n % 3) + 1)
    #自定义标签
    custom_tags = {
        'Environment': 'Development',
        'Department': 'IT'
    }
    #从官方获得的虚拟机镜像
    publisher_name = 'OpenLogic'
    offer = 'CentOS'
    sku = '7_9-gen2'
    version = 'latest'  # 使用最新版本
    #dsv5 1:4
    #dlsv5 1:2
    #esv5 1:8

    '''
    Standard_LRS 表示 Standard HDD
    StandardSSD_LRS 表示 Standard SSD
    Premium_LRS 表示 Premium SSD
    PremiumV2_LRS 表示SSD v2
    '''

    #操作系统盘只能是Premium_LRS和Standard_LRS
    os_disk_sku = "Premium_LRS"
    os_disk_name = vm_name + "-os-disk"
    os_disk_size_gb = 100

    #数据盘只能是Premium_LRS，Standard_LRS，PremiumV2_LRS
    data_disk01_name = vm_name + "-datadisk01"
    data_disk01_sku = "PremiumV2_LRS"

    data_disk02_name = vm_name + "-datadisk02"
    data_disk02_sku = "PremiumV2_LRS"


    #数据盘的容量大小，单位GB
    data_disk_size_gb = 1024
    #数据盘的IOPS
    data_disk_iops = 3000
    #数据盘的吞吐量
    data_disk_mbps = 125

    # sig_name = "nio_pe_image_template_fk"
    # sig_img_name = "Rocky9-Cloud-Init-PE"
    # sig_img_ver_name = "latest"

    sig_name = "nio_image_template_fk"
    sig_img_name = "rocky9"
    sig_img_ver_name = "latest"

    #SSH Key名称
    ssh_public_key_name = "pedevops2024"

    #网卡的安全组名称
    nic_nsgname = vm_name + "-nsg"

    #proximityPlacementGroups，请注意PPG保证多台虚拟机在同一个数据中心，相距的物理位置更近，但是不是高可用方案
    #ppg_name="lei-ppg"
    # Azure 信息
    # tenant_id = "72f988bf-86f1-41af-91ab-2d7cd011db47"
    # client_id = "a4cecf84-6569-40ba-980b-8fa823e6dda8"
    # certificate_path = r"D:\Work\Doc\sdp-app.pem"

    # 使用证书认证
    # clientcredential = CertificateCredential(
    #     tenant_id=tenant_id,
    #     client_id=client_id,
    #     certificate_path=certificate_path  # 证书路径
    # )
    # Create tenant_id

    clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)
    

    network_client = NetworkManagementClient(
        credential = clientcredential,
        subscription_id = sub_id
    )

    compute_client = ComputeManagementClient(
        credential = clientcredential,
        subscription_id = sub_id
    )
    ################################
    ###  1.先判断虚拟机是否存在，存在则直接退出
    ################################
    try:
        exist = compute_client.virtual_machines.get(rg_name,vm_name)
        print(f"虚拟机 '{vm_name}' 存在。")
        sys.exit(0)
    except ResourceNotFoundError:

        ################################
        ###  1.先获得SSH Key
        ################################
        # ssh_key = compute_client.ssh_public_keys.get(rg_name,ssh_public_key_name)
        # ssh_public_key = ssh_key.public_key


        ################################
        ###  3.创建数据盘01
        ###  这里先指定数据盘为空盘
        ###  默认情况下，高级 SSD v2 支持 4k 物理扇区大小，但也可以配置为使用 512 字节扇区大小。 
        ###  大多数应用程序都与 4k 扇区大小兼容，但某些应用程序需要 512 字节扇区大小。 
        ###  例如，Oracle Database 需要 12.2 版或更高版本才能支持 4k 本机磁盘。
        ################################
        '''
        start_time = time.time()
        data_disk01 = compute_client.disks.begin_create_or_update(
            resource_group_name = rg_name,
            disk_name = data_disk01_name,
            disk = {
                "location": location,
                "zones": [
                    availabiltiy_zone
                ],
                "sku": {
                    "name": data_disk01_sku 
                },
                "creation_data": {
                    "create_option": "Empty",
                    # 这里指定扇区大小为512 字节
                    "logical_sector_size": 512
                },
                "disk_size_gb": data_disk_size_gb,
                "disk_iops_read_write": data_disk_iops,
                "disk_m_bps_read_write": data_disk_mbps
            }
        ).result()
        print("--- %s seconds ---" % (time.time() - start_time))
        print("Create data disk 01:")
        '''
        ################################
        ###  4.创建数据盘02
        ################################
        '''
        start_time = time.time()
        data_disk02 = compute_client.disks.begin_create_or_update(
            resource_group_name = rg_name,
            disk_name = data_disk02_name,
            disk = {
                "location": location,
                "zones": [
                    availabiltiy_zone
                ],
                "sku": {
                    "name": data_disk02_sku
                },
                "creation_data": {
                    "create_option": "Empty",
                    # 这里指定扇区大小为512 字节
                    "logical_sector_size": 512
                },
                "disk_size_gb": data_disk_size_gb,
                "disk_iops_read_write": data_disk_iops,
                "disk_m_bps_read_write": data_disk_mbps
            }
        ).result()

        print("--- %s seconds ---" % (time.time() - start_time))
        print("Create data disk 02:")
        '''
        ################################
        #5.创建安全组
        ################################
        # start_time = time.time()
        # nic_nsg_result = network_client.network_security_groups.begin_create_or_update(
        #     rg_name,
        #     nic_nsgname,
        #     {
        #         'location': location,
        #         'security_rules': [
        #             {
        #                 'name': 'Allow-Internet-HTTP-Inbound',
        #                 'protocol': 'Tcp',
        #                 'direction': 'Inbound',
        #                 'source_address_prefix': '*',
        #                 'destination_address_prefix': '*',
        #                 'access': 'Allow',
        #                 'destination_port_range': '80',
        #                 'source_port_range': '*',
        #                 'priority': 3000
        #             },
        #             {
        #                 'name': 'Allow-Internet-HTTPS-Inbound',
        #                 'protocol': 'Tcp',
        #                 'direction': 'Inbound',
        #                 'source_address_prefix': '*',
        #                 'destination_address_prefix': '*',
        #                 'access': 'Allow',
        #                 'destination_port_range': '443',
        #                 'source_port_range': '*',
        #                 'priority': 3001
        #             }
        #         ]
        #     }
        # ).result()
        # print("--- %s seconds ---" % (time.time() - start_time))
        # print("Create NIC Network Security Group:")

        ################################
        #6.创建网卡，并附加安全组
        ################################

        start_time = time.time()
        nic = network_client.network_interfaces.begin_create_or_update(
            resource_group_name = rg_name,
            network_interface_name = nic_name,
            parameters = {
                "location": location,
                "ip_configurations": [{
                    "name": "nic-ip-config",
                    "subnet": {
                        "id": "/subscriptions/" + sub_id + "/resourceGroups/" + rg_name + "/providers/Microsoft.Network/virtualNetworks/" + vnet_name + "/subnets/" + subnet_name
                    },
                    "private_ip_allocation_method": "Dynamic"
                }],
                #先不使用网卡的安全组，所以把下面的内容注释掉

                # "network_security_group": {
                #     'id': nic_nsg_result.id
                #     #/subscriptions/c4959ac6-4963-4b67-90dd-da46865b607f/resourceGroups/DEFAULTRG/providers/Microsoft.Network/networkSecurityGroups/NIO_PE_OPS
                # },
                "enable_accelerated_networking": True,
                "tags": custom_tags
            }
        ).result()
        print("--- %s seconds ---" % (time.time() - start_time))
        print("Created NIC:\n{}".format(nic))



        ################################
        #7.创建虚拟机
        ################################
        start_time = time.time()
        vm = compute_client.virtual_machines.begin_create_or_update(
            resource_group_name = rg_name,
            vm_name = vm_name,
            parameters = {
                "location": location,
                #从get_gallery_image里获得的publisher,name, product，动态的填入下面的plan里
                #如果是ubuntu环境，则把plan内容全部去掉
                #如果是rocky环境，则不需要注释下面的环境，具体可以参考get_gallery_image.py
                # "plan": {
                # "name": "9-base",
                # "product": "rockylinux-x86_64",
                # "publisher": "resf"
                # },
                "zones": [
                    availability_zone
                ],
                "hardware_profile": {
                    "vm_size": vm_size
                },
                "storage_profile": {
                    "image_reference": {
                        #"id": "/subscriptions/" + sub_id + "/resourceGroups/" + rg_name + "/providers/Microsoft.Compute/galleries/" + sig_name + "/images/" + sig_img_name + "/versions/" + sig_img_ver_name
                        "publisher": publisher_name,
                        "offer": offer,
                        "sku": sku,
                        "version": version
                    },
                    "os_disk": {
                        "os_type": "Linux",
                        "name": os_disk_name,
                        "caching": "None",
                        "create_option": "FromImage",
                        "disk_size_gb": os_disk_size_gb,
                        "managed_disk": {
                            "storage_account_type": os_disk_sku
                        },
                        "delete_option": "Delete",
                        "tags": custom_tags
                    },
                    # "data_disks": [
                    #     #第一块数据盘
                    #     {
                    #         "lun": 0,
                    #         "name": data_disk01_name,
                    #         "caching": "None",  #"ReadOnly"
                    #         "create_option": "Attach",                    
                    #         "managed_disk": {
                    #             "id": "/subscriptions/" + sub_id + "/resourcegroups/" + rg_name + "/providers/Microsoft.Compute/disks/" + data_disk01_name
                    #     },
                    #         "delete_option": "Delete",
                    #         "tags": custom_tags
                    #     },
                    #     #第二块数据盘
                    #     {
                    #         "lun": 1,
                    #         "name": data_disk02_name,
                    #         "caching": "None",  #"ReadOnly"
                    #         "create_option": "Attach",                    
                    #         "managed_disk": {
                    #             "id": "/subscriptions/" + sub_id + "/resourcegroups/" + rg_name + "/providers/Microsoft.Compute/disks/" + data_disk02_name
                    #     },
                    #         "delete_option": "Delete",
                    #         "tags": custom_tags
                    #     }
                    # ]
                },
                "additional_capabilities": {
                    #"ultra_ssd_enabled": True
                    "ultra_ssd_enabled": False
                },
                "os_profile": {
                    "computer_name": computer_name,
                    "admin_username": "testuser",
                    "admin_password": "abc@123456$%^&*"
                },
                "network_profile": {
                    "network_interfaces": [
                        {
                            "id": "/subscriptions/" + sub_id + "/resourceGroups/" + rg_name + "/providers/Microsoft.Network/networkInterfaces/" + nic_name,
                            "primary": True,
                            "delete_option": "Delete"
                        }
                    ]
                },
                "diagnostics_profile": {
                    "boot_diagnostics": {
                        "enabled": True
                    }
                },
                # 请注意PPG保证多台虚拟机在同一个数据中心，相距的物理位置更近，但是不是高可用方案
                #'proximity_placement_group':{
                #    "id": "/subscriptions/" + sub_id + "/resourceGroups/" + rg_name + "/providers/Microsoft.Compute/proximityPlacementGroups/" + ppg_name

                #},
                "tags": custom_tags,
                "virtual_machine_scale_set": {
                    "id": "/subscriptions/" + sub_id + "/resourceGroups/" + rg_name + "/providers/Microsoft.Compute/virtualMachineScaleSets/" + vmss_name
                }
            }
        ).result()
        print("--- %s seconds ---" % (time.time() - start_time))
        print("Created VM:\n{}".format(vm))

        ################################
        #8.把这个虚拟机的内网ip打印出来
        ################################
        # 获取虚拟机信息
        vm = compute_client.virtual_machines.get(rg_name, vm_name)
        
        # 获取虚拟机的网络接口 ID
        nic_id = vm.network_profile.network_interfaces[0].id
        
        # 提取网络接口的名称和资源组名称
        nic_name = nic_id.split('/')[-1]
        nic_resource_group = nic_id.split('/')[4]
        
        # 获取网络接口信息
        nic = network_client.network_interfaces.get(nic_resource_group, nic_name)
        
        # 获取内网 IP 地址
        private_ip_address = nic.ip_configurations[0].private_ip_address
        
        print(f"虚拟机 '{vm_name}' 的内网 IP 地址是: {private_ip_address}")

def main():
    #50个线程
    with ThreadPoolExecutor(max_workers=50) as executor:
        #创建10台虚拟机
        futures = [executor.submit(create_vm, i) for i in range(0,400)]
        for future in futures:
            print(future.result())


if __name__ == "__main__":
    main()