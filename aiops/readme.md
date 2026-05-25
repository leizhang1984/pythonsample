AI Ops说明文档：

一.服务能力

1. 通过自然语言提问：请帮我看一下，10.94.109.31这台虚拟机，在北京时间2026年5月19日上午8点50分有没有问题
2. 把上面的问题进行分析，通过Azure Resource Graph Explorer查询到ip对应的虚拟机
3. 基于Azure Resource Health健康日志，Activity Log活动日志、Azure Monitor等指标，检查虚拟机是否有性能问题
4. Azure Monitor中的指标有：
   1. Percentage CPU，CPU使用率
   2. Available Memory Percentage，可用内存百分比
   3. VmAvailabilityMetric，VM平台可用性状态
   4. OS Disk Bandwidth Consumed Percentage，操作系统磁盘的带宽使用百分比
   5. OS Disk IOPS Consumed Percentage，操作系统磁盘的IOPS使用百分比
   6. Data Disk Bandwidth Consumed Percentage，数据磁盘的带宽使用百分比
   7. Data Disk IOPS Consumed Percentage，数据磁盘的IOPS使用百分比
   8. OS Disk Queue Depth，系统盘队列深度
   9. Data Disk Queue Depth，数据盘队列深度
   10. VM Uncached Bandwidth Consumed Percentage，虚拟机未缓存的带宽使用百分比，来判断虚拟机是否有到磁盘的带宽瓶颈
   11. VM Uncached IOPS Consumed Percentage，虚拟机未缓存的IOPS使用百分比，来判断虚拟机是否有到磁盘的IOPS瓶颈
   12. OS Disk Latency，操作系统磁盘延迟
   13. Data Disk Latency，数据盘延迟
5. 通过把这些事件和指标发送给azure AI foundary，通过AI来决策是否虚拟机有性能问题



二.部署文档

1. 请先创建服务账户Service Principal，请先登录azure控制台: https://portal.azure.com

2. 搜索entra id

   ![](https://github.com/leizhang1984/pythonsample/blob/main/aiops/images/1entra.png)

​	3.页面跳转后，点击下图的App Registration，点击New Registration

![](https://github.com/leizhang1984/pythonsample/blob/main/aiops/images/2app-registration.png)

​	3.输入app 名称

![](https://github.com/leizhang1984/pythonsample/blob/main/aiops/images/3newapp.png)

​	4.输入app secret，如下图：

**请保留下面的secret的值，后续需要使用**

![](https://github.com/leizhang1984/pythonsample/blob/main/aiops/images/4newsecret.png)

​	5.输入完毕后，就有三个值：

​	**Application id、tenant id、还有app key**

![](https://github.com/leizhang1984/pythonsample/blob/main/aiops/images/5sp.png)

​	6.然后我们分配权限，选择对应的管理组或者订阅，如下图：

![](https://github.com/leizhang1984/pythonsample/blob/main/aiops/images/6assign.png)

​	7.分配reader权限

![](https://github.com/leizhang1984/pythonsample/blob/main/aiops/images/7reader.png)

​	8.找到之前创建的服务账户

![](https://github.com/leizhang1984/pythonsample/blob/main/aiops/images/8assign-reader.png)

​	9.然后创建azure ai foundary，步骤略

![](https://github.com/leizhang1984/pythonsample/blob/main/aiops/images/9foundry.png)

​	10.在ai foundary里部署模型，这里模型名称为：gpt-5.4

​	11.拿到ai foundary的api key。如下图：

![](https://github.com/leizhang1984/pythonsample/blob/main/aiops/images/10foundrykey.png)





三.运行环境

1. 用vscode代码aiops.py
2. 把上面步骤2-5里面的application id, tenant id和app key更新到ai代码：
   1. 417行中，tenant id 
   2. 418行中，client id就是application id
   3. 419行中，client_secret就是app key
3. 修改ai foundary
   1. 26行，更新ai_foundry_endpoint
   2. 28行，更新你的模型
   3. 30行，输入的ai foundry的key

​	4.修改提示词，在第24行

​	



四.执行结果：

1. 执行后，会在aiops.py里，产生txt文件，包含以下内容:

我给出的专家结论是：

这台 Azure 虚拟机 **XXXXXXXX**（规格 **Standard_D8ls_v5**）在 **2026-05-19 08:45 ~ 09:15（北京时间）** 期间，出现了非常明确的 **主机内资源竞争型性能瓶颈**，且**核心瓶颈不是 Azure 平台可用性，也不是磁盘预配性能上限被打满，而是虚拟机内部 CPU 与内存资源耗尽，继发导致 OS 层磁盘响应异常**。

更具体的内容，略。