import ipaddress
import json
import time
from collections import defaultdict
from contextlib import ExitStack
from uuid import UUID

from azure.core.exceptions import AzureError
from azure.identity import ClientSecretCredential
from azure.mgmt.compute import ComputeManagementClient
from azure.mgmt.network import NetworkManagementClient
from azure.mgmt.resource import ResourceManagementClient
from azure.mgmt.resource.resources.models import Tags, TagsPatchResource
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import QueryRequest, QueryRequestOptions


# ==================== 配置区域 ====================

TENANT_ID = ""
CLIENT_ID = ""
CLIENT_SECRET = ""

# 私有 IP，多个使用分号分隔。
IP_STRING = "10.180.1.4;10.180.1.5;10.180.1.6;10.180.1.7;10.180.1.8;10.180.1.9"

# 明确限定查询范围，多个订阅使用分号分隔。
SUBSCRIPTION_STRING = "" 

# 同名标签更新，不存在的标签新增，其他标签保留。
TAGS_TO_SET = {
    "application": "redis",
    "environment": "production",
    "costcenter": "S00001",
    "owner": "leizhang",
}

# False：只预览，不修改。
# True：直接执行标签合并，不进行交互确认。
APPLY_CHANGES = True

# ==================================================


def normalize_id(resource_id):
    return resource_id.rstrip("/").lower()


def parse_resource_id(resource_id):
    parts = resource_id.strip("/").split("/")

    if (
        len(parts) != 8
        or parts[0].lower() != "subscriptions"
        or parts[2].lower() != "resourcegroups"
        or parts[4].lower() != "providers"
    ):
        raise ValueError(f"不支持的资源 ID：{resource_id}")

    return parts[1], parts[3], parts[7]


def parse_ips(value):
    ips = list(dict.fromkeys(
        str(ipaddress.ip_address(item.strip()))
        for item in value.split(";")
        if item.strip()
    ))

    if not ips:
        raise ValueError("IP_STRING 至少需要一个有效 IP。")

    return ips


def parse_subscriptions(value):
    subscriptions = list(dict.fromkeys(
        str(UUID(item.strip()))
        for item in value.split(";")
        if item.strip()
    ))

    if not subscriptions:
        raise ValueError("请至少配置一个订阅 ID。")

    return subscriptions


def validate_tags(tags):
    if not isinstance(tags, dict) or not tags:
        raise ValueError("TAGS_TO_SET 必须是非空字典。")

    if len(tags) > 50:
        raise ValueError("本次设置的标签数量不能超过 50 个。")

    forbidden = set("<>%&\\?/")

    for key, value in tags.items():
        if not isinstance(key, str) or not key.strip():
            raise ValueError("标签名称必须是非空字符串。")

        if len(key) > 512 or any(char in forbidden for char in key):
            raise ValueError(f"标签名称长度或字符不合法：{key}")

        if not isinstance(value, str) or len(value) > 256:
            raise ValueError(
                f"标签值必须是长度不超过 256 的字符串：{key}"
            )

    keys = [key.lower() for key in tags]
    if len(keys) != len(set(keys)):
        raise ValueError("存在仅大小写不同的重复标签名称。")

    return dict(tags)


class AzureClients:
    """按订阅复用客户端和连接。"""

    def __init__(self, credential):
        self.credential = credential
        self.stack = ExitStack()
        self.compute_clients = {}
        self.network_clients = {}
        self.resource_clients = {}

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        return self.stack.__exit__(exc_type, exc_value, traceback)

    def compute(self, subscription_id):
        key = subscription_id.lower()

        if key not in self.compute_clients:
            self.compute_clients[key] = self.stack.enter_context(
                ComputeManagementClient(
                    self.credential,
                    subscription_id,
                )
            )

        return self.compute_clients[key]

    def network(self, subscription_id):
        key = subscription_id.lower()

        if key not in self.network_clients:
            self.network_clients[key] = self.stack.enter_context(
                NetworkManagementClient(
                    self.credential,
                    subscription_id,
                )
            )

        return self.network_clients[key]

    def resources(self, subscription_id):
        key = subscription_id.lower()

        if key not in self.resource_clients:
            self.resource_clients[key] = self.stack.enter_context(
                ResourceManagementClient(
                    self.credential,
                    subscription_id,
                )
            )

        return self.resource_clients[key]


def find_vm_matches(credential, subscriptions, ips):
    matches = {ip: set() for ip in ips}
    started = time.perf_counter()

    with ResourceGraphClient(credential) as graph:
        for ip_start in range(0, len(ips), 100):
            ip_batch = ips[ip_start:ip_start + 100]

            ip_literals = ", ".join(
                f"'{ip}'" for ip in ip_batch
            )

            # 先筛选候选网卡，再展开 IP 配置并精确匹配。
            candidate_filter = " or ".join(
                f"tostring(ipConfigs) contains '{ip}'"
                for ip in ip_batch
            )

            query = f"""
Resources
| where type =~ 'microsoft.network/networkinterfaces'
| where isnotempty(properties.virtualMachine.id)
| project
    id,
    vmId = tostring(properties.virtualMachine.id),
    ipConfigs = properties.ipConfigurations
| where {candidate_filter}
| mv-expand ipconfig = ipConfigs
| extend privateIp = tostring(ipconfig.properties.privateIPAddress)
| where privateIp in ({ip_literals})
| project id, privateIp, vmId
"""

            for sub_start in range(0, len(subscriptions), 100):
                sub_batch = subscriptions[sub_start:sub_start + 100]
                skip_token = None

                while True:
                    request_started = time.perf_counter()

                    result = graph.resources(
                        QueryRequest(
                            subscriptions=sub_batch,
                            query=query,
                            options=QueryRequestOptions(
                                result_format="objectArray",
                                top=1000,
                                skip_token=skip_token,
                            ),
                        )
                    )

                    print(
                        f"Resource Graph：{len(sub_batch)} 个订阅，"
                        f"{len(ip_batch)} 个 IP，"
                        f"返回 {len(result.data)} 条，"
                        f"耗时 "
                        f"{time.perf_counter() - request_started:.2f} 秒",
                        flush=True,
                    )

                    for row in result.data:
                        matches[row["privateIp"]].add(
                            normalize_id(row["vmId"])
                        )

                    skip_token = result.skip_token

                    if not skip_token:
                        truncated = getattr(
                            result.result_truncated,
                            "value",
                            result.result_truncated,
                        )

                        if str(truncated).lower() == "true":
                            raise RuntimeError(
                                "查询结果被截断且无分页令牌，"
                                "无法完整判断 IP 唯一性，停止操作。"
                            )

                        break

    problems = []

    for ip, vm_ids in matches.items():
        if not vm_ids:
            problems.append(f"{ip}：没有找到对应虚拟机。")
        elif len(vm_ids) > 1:
            problems.append(
                f"{ip}：匹配多台虚拟机，不能唯一确定目标：\n"
                + "\n".join(sorted(vm_ids))
            )

    if problems:
        raise RuntimeError(
            "资源发现未通过，未修改标签：\n"
            + "\n".join(problems)
        )

    vm_ips = defaultdict(list)

    for ip, vm_ids in matches.items():
        vm_ips[next(iter(vm_ids))].append(ip)

    print(
        f"\nResource Graph 完成："
        f"{len(ips)} 个 IP 对应 {len(vm_ips)} 台虚拟机，"
        f"总耗时 {time.perf_counter() - started:.2f} 秒",
        flush=True,
    )

    return vm_ips


def get_exclusive_resources(clients, vm_id, expected_ips):
    subscription_id, resource_group, vm_name = parse_resource_id(vm_id)

    compute = clients.compute(subscription_id)
    network = clients.network(subscription_id)

    vm = compute.virtual_machines.get(
        resource_group,
        vm_name,
    )

    resources = [{
        "id": vm.id,
        "type": "virtualMachine",
        "vm_id": vm.id,
    }]

    actual_ips = set()

    # 遍历全部网卡以及每块网卡的全部 IP 配置。
    for nic_ref in vm.network_profile.network_interfaces or []:
        nic_sub, nic_group, nic_name = parse_resource_id(nic_ref.id)

        if nic_sub.lower() != subscription_id.lower():
            raise RuntimeError(f"发现跨订阅网卡：{nic_ref.id}")

        nic = network.network_interfaces.get(
            nic_group,
            nic_name,
        )

        if (
            not nic.virtual_machine
            or normalize_id(nic.virtual_machine.id)
            != normalize_id(vm.id)
        ):
            raise RuntimeError(f"网卡归属不一致：{nic.id}")

        resources.append({
            "id": nic.id,
            "type": "networkInterface",
            "vm_id": vm.id,
        })

        for config in nic.ip_configurations or []:
            if config.private_ip_address:
                actual_ips.add(
                    str(ipaddress.ip_address(config.private_ip_address))
                )

            public_ip_ref = config.public_ip_address

            if not public_ip_ref or not public_ip_ref.id:
                continue

            pip_sub, pip_group, pip_name = parse_resource_id(
                public_ip_ref.id
            )

            public_ip = clients.network(
                pip_sub
            ).public_ip_addresses.get(
                pip_group,
                pip_name,
            )

            # 反向确认公网 IP 绑定当前网卡的 IP 配置。
            bound_config = public_ip.ip_configuration

            if (
                not config.id
                or not bound_config
                or not bound_config.id
                or normalize_id(bound_config.id)
                != normalize_id(config.id)
            ):
                raise RuntimeError(
                    f"公网 IP 归属不一致：{public_ip.id}"
                )

            if public_ip.nat_gateway:
                raise RuntimeError(
                    f"公网 IP 关联 NAT 网关，"
                    f"不属于预期单机独享资源：{public_ip.id}"
                )

            resources.append({
                "id": public_ip.id,
                "type": "publicIPAddress",
                "vm_id": vm.id,
            })

    # 使用当前网卡信息核对 Resource Graph 中发现的私有 IP。
    if not set(expected_ips).issubset(actual_ips):
        raise RuntimeError(
            f"输入 IP 已不属于该虚拟机，请重新查询：{vm.id}"
        )

    storage = vm.storage_profile
    disks = [("osDisk", storage.os_disk)]
    disks.extend(
        ("dataDisk", disk)
        for disk in storage.data_disks or []
    )

    for disk_type, disk_ref in disks:
        diff = getattr(disk_ref, "diff_disk_settings", None)
        option = getattr(diff, "option", None)
        option = getattr(option, "value", option)

        if str(option).lower() == "local":
            print(
                f"跳过临时 OS 磁盘，无独立磁盘资源：{vm.name}",
                flush=True,
            )
            continue

        managed_disk = getattr(disk_ref, "managed_disk", None)

        if not managed_disk or not managed_disk.id:
            raise RuntimeError(
                f"发现非托管或不支持的磁盘：{disk_ref.name}，"
                f"VM={vm.id}。请人工确认。"
            )

        disk_sub, disk_group, disk_name = parse_resource_id(
            managed_disk.id
        )

        if disk_sub.lower() != subscription_id.lower():
            raise RuntimeError(
                f"发现跨订阅磁盘：{managed_disk.id}"
            )

        disk = compute.disks.get(
            disk_group,
            disk_name,
        )

        owners = {
            normalize_id(owner)
            for owner in [
                disk.managed_by,
                *(disk.managed_by_extended or []),
            ]
            if owner
        }

        # 允许多机共享的磁盘不纳入，即使目前仅挂载一台 VM。
        if (disk.max_shares or 1) > 1 or len(owners) > 1:
            print(f"跳过共享磁盘：{disk.id}", flush=True)
            continue

        if owners != {normalize_id(vm.id)}:
            raise RuntimeError(f"磁盘归属不一致：{disk.id}")

        resources.append({
            "id": disk.id,
            "type": disk_type,
            "vm_id": vm.id,
        })

    return resources


def build_plan(clients, vm_ips):
    plan = {}
    started = time.perf_counter()

    for index, (vm_id, ips) in enumerate(vm_ips.items(), start=1):
        subscription_id, resource_group, vm_name = parse_resource_id(vm_id)
        vm_started = time.perf_counter()

        print(
            f"\n[{index}/{len(vm_ips)}] 虚拟机：{vm_name}\n"
            f"订阅：{subscription_id}\n"
            f"资源组：{resource_group}\n"
            f"输入 IP：{';'.join(ips)}",
            flush=True,
        )

        resources = get_exclusive_resources(
            clients,
            vm_id,
            ips,
        )

        for resource in resources:
            key = normalize_id(resource["id"])

            if (
                key in plan
                and normalize_id(plan[key]["vm_id"])
                != normalize_id(resource["vm_id"])
            ):
                raise RuntimeError(
                    f"资源被多台选中虚拟机引用：{resource['id']}"
                )

            plan[key] = resource

        print(
            f"发现 {len(resources)} 个独享资源，"
            f"耗时 {time.perf_counter() - vm_started:.2f} 秒",
            flush=True,
        )

    print(
        f"\n资源遍历完成：共 {len(plan)} 个资源，"
        f"耗时 {time.perf_counter() - started:.2f} 秒",
        flush=True,
    )

    return list(plan.values())


def apply_tags(clients, plan, tags):
    completed = 0
    started = time.perf_counter()

    for index, resource in enumerate(plan, start=1):
        subscription_id, _, _ = parse_resource_id(resource["id"])
        client = clients.resources(subscription_id)

        try:
            # Merge：
            # 同名标签覆盖值；不存在的标签新增；其他标签保留。
            # 不读取旧标签，也不执行写后回读比较。
            client.tags.begin_update_at_scope(
                scope=resource["id"],
                parameters=TagsPatchResource(
                    operation="Merge",
                    properties=Tags(tags=dict(tags)),
                ),
            ).result()

        except AzureError as exc:
            raise RuntimeError(
                f"合并标签失败：{resource['id']}\n"
                f"此前已完成 {completed} 个资源。\n"
                "当前资源可能已经写入；停止后续操作，不自动回滚。"
            ) from exc

        completed += 1

        print(
            f"[{index}/{len(plan)}] 标签合并请求已完成："
            f"{resource['id']}",
            flush=True,
        )

    print(
        f"\n完成，共 {completed} 个资源，"
        f"耗时 {time.perf_counter() - started:.2f} 秒",
        flush=True,
    )


def main():
    if (
        not TENANT_ID.strip()
        or not CLIENT_ID.strip()
        or not CLIENT_SECRET.strip()
        or CLIENT_ID.startswith("填写")
        or CLIENT_SECRET.startswith("填写")
    ):
        raise ValueError(
            "请先填写 TENANT_ID、CLIENT_ID、CLIENT_SECRET。"
        )

    UUID(TENANT_ID)
    UUID(CLIENT_ID)

    ips = parse_ips(IP_STRING)
    subscriptions = parse_subscriptions(SUBSCRIPTION_STRING)
    tags = validate_tags(TAGS_TO_SET)

    with ClientSecretCredential(
        tenant_id=TENANT_ID,
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    ) as credential:
        vm_ips = find_vm_matches(
            credential,
            subscriptions,
            ips,
        )

        with AzureClients(credential) as clients:
            # 只遍历一次，完成全部发现后再写入。
            plan = build_plan(clients, vm_ips)

            print("\n待处理资源：")
            print(json.dumps(plan, ensure_ascii=False, indent=2))

            print("\n本次新增或更新的标签：")
            print(json.dumps(tags, ensure_ascii=False, indent=2))

            print("\n标签模式：Merge，保留其他原有标签。")

            if not APPLY_CHANGES:
                print("\n仅预览，未修改任何标签。")
                print("确认后设置 APPLY_CHANGES = True。")
                return

            apply_tags(clients, plan, tags)


if __name__ == "__main__":
    main()
