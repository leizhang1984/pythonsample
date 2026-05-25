AI Ops说明文档：

一.服务能力

1. 通过自然语言提问：请帮我看一下，10.94.109.31这台虚拟机，在北京时间2026年5月19日上午8点50分有没有问题
2. 把上面的问题进行分析，通过Azure Resource Graph Explorer查询到ip对应的虚拟机
3. 基于Azure Resource Health健康日志，Activity Log活动日志、Azure Monitor等指标，检查虚拟机是否有性能问题
4. Azure Monitor中的指标有：
   1. Percentage CPU
   2. Available Memory Percentage
   3. VmAvailabilityMetric
   4. OS Disk Bandwidth Consumed Percentage
   5. OS Disk IOPS Consumed Percentage
   6. Data Disk Bandwidth Consumed Percentage
   7. Data Disk IOPS Consumed Percentage
   8. OS Disk Queue Depth
   9. Data Disk Queue Depth
   10. VM Uncached Bandwidth Consumed Percentage
   11. VM Uncached IOPS Consumed Percentage
   12. Data Disk Latency
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

![](https://github.com/leizhang1984/pythonsample/blob/main/aiops/images/5sp.png)

​	6.然后我们分配权限，选择对应的管理组或者订阅，如下图：

![](https://github.com/leizhang1984/pythonsample/blob/main/aiops/images/6assign.png)

​	7.分配reader权限

![](https://github.com/leizhang1984/pythonsample/blob/main/aiops/images/7reader.png)

​	8.找到之前创建的服务账户

![](https://github.com/leizhang1984/pythonsample/blob/main/aiops/images/8assign-reader.png)

​	9.然后创建azure ai foundary，步骤略

​	10.在ai foundary里部署模型，这里模型名称为：gpt-5.4

​	11.拿到ai foundary的api key





三.运行环境

