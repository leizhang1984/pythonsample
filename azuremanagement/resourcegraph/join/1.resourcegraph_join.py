import os
from datetime import timedelta

#pip3 install azure-kusto-data
from azure.identity import ClientSecretCredential
from azure.mgmt.resourcegraph import ResourceGraphClient
from azure.mgmt.resourcegraph.models import *
import pandas as pd
'''
https://github.com/Azure-Samples/azure-samples-python-management/blob/main/samples/resourcegraph/resources_query.py
'''



tenantid = os.environ.get('nonprod_tenantid')
clientid = os.environ.get('nonprod_clientid')
clientsecret = os.environ.get('nonprod_clientsecret')

subscriptionid = "166157a8-9ce9-400b-91c7-1d42482b83d6"

clientcredential = ClientSecretCredential(tenantid,clientid,clientsecret)

# Create client
# For other authentication approaches, please see: https://pypi.org/project/azure-identity/
resourcegraph_client = ResourceGraphClient(
    credential = clientcredential,
    subscription_id = subscriptionid
)

# Query Azure Update Manager Machines
query1 = QueryRequest(
        query=f'''
        ((resources
        | where type =~ "microsoft.compute/virtualmachines"
        | extend imageRefHotpatch = properties.storageProfile.imageReference
        | extend isHotpatchCapable = case((imageRefHotpatch.publisher in~ ('microsoftwindowsserver') and imageRefHotpatch.offer in~ ('windowsserver','microsoftserveroperatingsystems-previews') and imageRefHotpatch.sku in~ ('2022-datacenter-azure-edition-core','2022-datacenter-azure-edition-core-smalldisk','2022-datacenter-azure-edition-hotpatch','2022-datacenter-azure-edition-hotpatch-smalldisk','windows-server-2025-azure-edition-hotpatch','2025-datacenter-azure-edition','2025-datacenter-azure-edition-core','2025-datacenter-azure-edition-core-smalldisk','2025-datacenter-azure-edition-smalldisk')), "Not Enrolled", "Not Available")
        | extend hotpatchStatus = case(isHotpatchCapable == "Not Available","Not Available",properties.osProfile.windowsConfiguration.patchSettings.enableHotpatching =~ "true", "Enabled","Disabled")
        | where properties.storageProfile.osDisk.osType in~ ('Linux','Windows')
        | extend os = tolower(properties.storageProfile.osDisk.osType)
        | extend patchSettingsObject = iff(os == "windows", properties.osProfile.windowsConfiguration.patchSettings, properties.osProfile.linuxConfiguration.patchSettings)
        | extend conf = tostring(patchSettingsObject.patchMode)
        | extend conf = iff (conf =~ "AutomaticByPlatform",
        iff(isnotnull(patchSettingsObject.automaticByPlatformSettings.bypassPlatformSafetyChecksOnUserSchedule) and patchSettingsObject.automaticByPlatformSettings.bypassPlatformSafetyChecksOnUserSchedule == true, "AutomaticByPlatformWithUserManagedSchedules", "AutomaticByPlatformUsingAutoGuestPatching"),conf)
        | extend assessMode = tostring(patchSettingsObject.assessmentMode)
        | extend periodicAssessment = iff(assessMode =~ "AutomaticByPlatform", "Yes", "No")
        | extend status=tostring(properties.extended.instanceView.powerState.displayStatus)
        | extend imageRef = strcat(tolower(tostring(properties.storageProfile.imageReference.publisher)), ":", tolower(tostring(properties.storageProfile.imageReference.offer)), ":", tolower(tostring(properties.storageProfile.imageReference.sku)))
        | extend isMarketplace = (isnotempty(properties.storageProfile.imageReference.publisher) and isnotempty(properties.storageProfile.imageReference.offer) and isnotempty(properties.storageProfile.imageReference.sku))
        | extend isNotInCRPAllowList = (isnotempty(properties.storageProfile.imageReference.publisher) and isnotempty(properties.storageProfile.imageReference.offer) and isnotempty(properties.storageProfile.imageReference.sku)) and not(iff(os =~ "windows", not(imageRef matches regex 'center-for-internet-security-inc:cis-windows-server:cis-windows-server-l.*-azure-observability') and (imageRef in ('center-for-internet-security-inc:cis-windows-server-2019-v1-0-0-l2:cis-ws2019-l2','center-for-internet-security-inc:cis-windows-server:cis-windows-server2019-l1-gen1','center-for-internet-security-inc:cis-windows-server:cis-windows-server2022-l1-gen1','center-for-internet-security-inc:cis-windows-server:cis-windows-server2022-l1-gen2','center-for-internet-security-inc:cis-windows-server:cis-windows-server2022-l2-gen2','center-for-internet-security-inc:cis-windows-server-2022-l2:cis-windows-server-2022-l2-gen2','microsoftwindowsserver:windowsserver:2008-r2-sp1','microsoftwindowsserver:windowsserver:2012-r2-datacenter','microsoftwindowsserver:windowsserver:2012-r2-datacenter-gensecond','microsoftwindowsserver:windowsserver:2012-r2-datacenter-smalldisk','microsoftwindowsserver:windowsserver:2012-r2-datacenter-smalldisk-g2','microsoftwindowsserver:windowsserver:2016-datacenter','microsoftwindowsserver:windowsserver:2016-datacenter-gensecond','microsoftwindowsserver:windowsserver:2016-datacenter-server-core','microsoftwindowsserver:windowsserver:2016-datacenter-smalldisk','microsoftwindowsserver:windowsserver:2016-datacenter-with-containers','microsoftwindowsserver:windowsserver:2019-datacenter','microsoftwindowsserver:windowsserver:2019-datacenter-core','microsoftwindowsserver:windowsserver:2019-datacenter-gensecond','microsoftwindowsserver:windowsserver:2019-datacenter-smalldisk','microsoftwindowsserver:windowsserver:2019-datacenter-smalldisk-g2','microsoftwindowsserver:windowsserver:2019-datacenter-with-containers','microsoftwindowsserver:windowsserver:2022-datacenter','microsoftwindowsserver:windowsserver:2022-datacenter-azure-edition','microsoftwindowsserver:windowsserver:2022-datacenter-azure-edition-core','microsoftwindowsserver:windowsserver:2022-datacenter-azure-edition-core-smalldisk','microsoftwindowsserver:windowsserver:2022-datacenter-azure-edition-hotpatch','microsoftwindowsserver:windowsserver:2022-datacenter-azure-edition-hotpatch-smalldisk','microsoftwindowsserver:windowsserver:2022-datacenter-azure-edition-smalldisk','microsoftwindowsserver:windowsserver:2022-datacenter-core','microsoftwindowsserver:windowsserver:2022-datacenter-core-g2','microsoftwindowsserver:windowsserver:2022-datacenter-g2','microsoftwindowsserver:windowsserver:2022-datacenter-smalldisk','microsoftwindowsserver:windowsserver:2022-datacenter-smalldisk-g2','microsoftwindowsserver:microsoftserveroperatingsystems-previews:windows-server-2025-azure-edition-hotpatch','microsoftwindowsserver:windowsserver:2025-datacenter-azure-edition','microsoftwindowsserver:windowsserver:2025-datacenter-azure-edition-core','microsoftwindowsserver:windowsserver:2025-datacenter-azure-edition-core-smalldisk','microsoftwindowsserver:windowsserver:2025-datacenter-azure-edition-smalldisk','microsoftazuresiterecovery:process-server:windows-2012-r2-datacenter','microsoftdynamicsax:dynamics:pre-req-ax7-onebox-v4','microsoftdynamicsax:dynamics:pre-req-ax7-onebox-v5','microsoftdynamicsax:dynamics:pre-req-ax7-onebox-v6','microsoftdynamicsax:dynamics:pre-req-ax7-onebox-v7','microsoftdynamicsax:dynamics:pre-req-ax7-onebox-u8','microsoftsqlserver:sql2016sp1-ws2016:standard','microsoftsqlserver:sql2016sp2-ws2016:standard','microsoftsqlserver:sql2017-ws2016:enterprise','microsoftsqlserver:sql2017-ws2016:standard','microsoftsqlserver:sql2019-ws2019:enterprise','microsoftsqlserver:sql2019-ws2019:sqldev','microsoftsqlserver:sql2019-ws2019:standard','microsoftsqlserver:sql2019-ws2019:standard-gen2','bissantechnology1583581147809:bissan_secure_windows_server2019:secureserver2019','center-for-internet-security-inc:cis-windows-server-2016-v1-0-0-l1:cis-ws2016-l1','center-for-internet-security-inc:cis-windows-server-2016-v1-0-0-l2:cis-ws2016-l2','center-for-internet-security-inc:cis-windows-server-2019-v1-0-0-l1:cis-ws2019-l1','center-for-internet-security-inc:cis-win-2016-stig:cis-win-2016-stig','center-for-internet-security-inc:cis-win-2019-stig:cis-win-2019-stig','center-for-internet-security-inc:cis-windows-server:cis-windows-server2019-stig-gen1','center-for-internet-security-inc:cis-windows-server-2012-r2-v2-2-1-l1:cis-ws2012-r2-l1','center-for-internet-security-inc:cis-windows-server-2012-r2-v2-2-1-l2:cis-ws2012-r2-l2','cloud-infrastructure-services:servercore-2019:servercore-2019','cloud-infrastructure-services:hpc2019-windows-server-2019:hpc2019-windows-server-2019','cognosys:sql-server-2016-sp2-std-win2016-debug-utilities:sql-server-2016-sp2-std-win2016-debug-utilities','cloud-infrastructure-services:ad-dc-2016:ad-dc-2016','cloud-infrastructure-services:ad-dc-2019:ad-dc-2019','cloud-infrastructure-services:ad-dc-2022:ad-dc-2022','cloud-infrastructure-services:sftp-2016:sftp-2016','cloud-infrastructure-services:rds-farm-2019:rds-farm-2019','cloud-infrastructure-services:hmailserver:hmailserver-email-server-2016','ntegralinc1586961136942:ntg_windows_datacenter_2019:ntg_windows_server_2019','outsystems:os11-vm-baseimage:platformserver','tidalmediainc:windows-server-2022-datacenter:windows-server-2022-datacenter','veeam:office365backup:veeamoffice365backup','microsoftdynamicsnav:dynamicsnav:2017','microsoftwindowsserver:windowsserver-hub:2012-r2-datacenter-hub','microsoftwindowsserver:windowsserver-hub:2016-datacenter-hub','aod:win2019azpolicy:win2019azpolicy') or imageRef matches regex 'microsoftwindowsserver:windowsserver:.*|microsoftbiztalkserver:biztalk-server:.*|microsoftdynamicsax:dynamics:.*|microsoftpowerbi:.*:.*|microsoftsharepoint:microsoftsharepointserver:.*|microsoftsqlserver:.*:.*|microsoftvisualstudio:visualstudio.*:.*-ws2012r2|microsoftvisualstudio:visualstudio.*:.*-ws2016|microsoftvisualstudio:visualstudio.*:.*-ws2019|microsoftvisualstudio:visualstudio.*:.*-ws2022|microsoftwindowsserver:windows-cvm:.*|microsoftwindowsserver:windowsserverdotnet:.*|microsoftwindowsserver:windowsserver-gen2preview:.*|microsoftwindowsserver:windowsserversemiannual:.*|microsoftwindowsserver:windowsserverupgrade:.*|microsoftwindowsserverhpcpack:windowsserverhpcpack:.*|microsoft-dsvm:dsvm-windows:.*|microsoft-dsvm:dsvm-win-2019:.*|microsoft-dsvm:dsvm-win-2022:.*|center-for-internet-security-inc:cis-windows-server:cis-windows-server2016-l.*|center-for-internet-security-inc:cis-windows-server:cis-windows-server2019-l.*|center-for-internet-security-inc:cis-windows-server:cis-windows-server2022-l.*|center-for-internet-security-inc:cis-windows-server-2022-l1:.*|center-for-internet-security-inc:cis-windows-server-2022-l2:.*|microsoft-ads:windows-data-science-vm:.*|filemagellc:filemage-gateway-vm-win:filemage-gateway-vm-win-.*|esri:arcgis-enterprise.*:byol.*|esri:pro-byol:pro-byol-.*|veeam:veeam-backup-replication:veeam-backup-replication-v.*|southrivertech1586314123192:tn-ent-payg:tnentpayg.*|belindaczsro1588885355210:belvmsrv.*:belvmsrv.*|southrivertech1586314123192:tn-sftp-payg:tnsftppayg.*'), not(imageRef in ('redhat:rhel-ha:81_gen2') or imageRef matches regex 'openlogic:centos:8.*|openlogic:centos-hpc:.*|microsoftsqlserver:sql2019-sles.*:.*|microsoftsqlserver:sql2019-rhel7:.*|microsoftsqlserver:sql2017-rhel7:.*|microsoft-ads:.*:.*') and (imageRef in ('almalinux:almalinux-hpc:8-hpc-gen2','almalinux:almalinux-hpc:8_5-hpc','almalinux:almalinux-hpc:8_5-hpc-gen2','almalinux:almalinux-hpc:8_6-hpc','almalinux:almalinux-hpc:8_6-hpc-gen2','almalinux:almalinux-hpc:8_7-hpc-gen1','almalinux:almalinux-hpc:8_7-hpc-gen2','canonical:ubuntuserver:16.04-lts','canonical:ubuntuserver:16.04.0-lts','canonical:ubuntuserver:18.04-lts','canonical:ubuntuserver:18_04-lts-arm64','canonical:ubuntuserver:18_04-lts-gen2','canonical:0001-com-ubuntu-confidential-vm-focal:20_04-lts-cvm','canonical:0001-com-ubuntu-confidential-vm-jammy:22_04-lts-cvm','canonical:0001-com-ubuntu-pro-bionic:pro-18_04-lts','canonical:0001-com-ubuntu-pro-focal:pro-20_04-lts','canonical:0001-com-ubuntu-pro-focal:pro-20_04-lts-gen2','canonical:0001-com-ubuntu-pro-jammy:pro-22_04-lts-gen2','canonical:0001-com-ubuntu-server-focal:20_04-lts','canonical:0001-com-ubuntu-server-focal:20_04-lts-gen2','canonical:0001-com-ubuntu-server-focal:20_04-lts-arm64','canonical:0001-com-ubuntu-server-jammy:22_04-lts','canonical:0001-com-ubuntu-server-jammy:22_04-lts-arm64','canonical:0001-com-ubuntu-server-jammy:22_04-lts-gen2','center-for-internet-security-inc:cis-rhel-7-v2-2-0-l1:cis-redhat7-l1','center-for-internet-security-inc:cis-rhel:cis-redhat8-l1-gen1','center-for-internet-security-inc:cis-rhel:cis-redhat8-l2-gen1','center-for-internet-security-inc:cis-rhel:cis-redhat9-l1-gen2','center-for-internet-security-inc:cis-ubuntu-linux-2004-l1:cis-ubuntu-linux-2004-l1','center-for-internet-security-inc:cis-ubuntu-linux-2204-l1:cis-ubuntu-linux-2204-l1','center-for-internet-security-inc:cis-ubuntu:cis-ubuntulinux2004-l1-gen1','center-for-internet-security-inc:cis-ubuntu:cis-ubuntulinux2204-l1-gen2','microsoftcblmariner:cbl-mariner:cbl-mariner-1','microsoftcblmariner:cbl-mariner:1-gen2','microsoftcblmariner:cbl-mariner:cbl-mariner-2','microsoftcblmariner:cbl-mariner:cbl-mariner-2-arm64','microsoftcblmariner:cbl-mariner:cbl-mariner-2-gen2','microsoftcblmariner:cbl-mariner:cbl-mariner-2-gen2-fips','microsoft-aks:aks:aks-engine-ubuntu-1804-202112','microsoft-dsvm:aml-workstation:ubuntu-20','microsoft-dsvm:aml-workstation:ubuntu-20-gen2','microsoft-dsvm:ubuntu-hpc:1804','microsoft-dsvm:ubuntu-hpc:1804-ncv4','microsoft-dsvm:ubuntu-hpc:2004','microsoft-dsvm:ubuntu-hpc:2004-preview-ndv5','microsoft-dsvm:ubuntu-hpc:2204','microsoft-dsvm:ubuntu-hpc:2204-preview-ndv5','openlogic:centos:7.2','openlogic:centos:7.3','openlogic:centos:7.4','openlogic:centos:7.5','openlogic:centos:7.6','openlogic:centos:7.7','openlogic:centos:7_8','openlogic:centos:7_9','openlogic:centos:7_9-gen2','openlogic:centos:8.0','openlogic:centos:8_1','openlogic:centos:8_2','openlogic:centos:8_3','openlogic:centos:8_4','openlogic:centos:8_5','openlogic:centos-lvm:7-lvm','openlogic:centos-lvm:8-lvm','redhat:rhel:7.2','redhat:rhel:7.3','redhat:rhel:7.4','redhat:rhel:7.5','redhat:rhel:7.6','redhat:rhel:7.7','redhat:rhel:7.8','redhat:rhel:7_9','redhat:rhel:7-lvm','redhat:rhel:7-raw','redhat:rhel:8','redhat:rhel:8.1','redhat:rhel:81gen2','redhat:rhel:8.2','redhat:rhel:82gen2','redhat:rhel:8_3','redhat:rhel:83-gen2','redhat:rhel:8_4','redhat:rhel:84-gen2','redhat:rhel:8_5','redhat:rhel:85-gen2','redhat:rhel:8_6','redhat:rhel:86-gen2','redhat:rhel:8_7','redhat:rhel:8_8','redhat:rhel:8-lvm','redhat:rhel:8-lvm-gen2','redhat:rhel-raw:8-raw','redhat:rhel-raw:8-raw-gen2','redhat:rhel:9_0','redhat:rhel:9_1','redhat:rhel:9-lvm','redhat:rhel:9-lvm-gen2','redhat:rhel-arm64:8_6-arm64','redhat:rhel-arm64:9_0-arm64','redhat:rhel-arm64:9_1-arm64','suse:sles-12-sp5:gen1','suse:sles-12-sp5:gen2','suse:sles-15-sp2:gen1','suse:sles-15-sp2:gen2','almalinux:almalinux-x86_64:8_7-gen2','aviatrix-systems:aviatrix-bundle-payg:aviatrix-enterprise-bundle-byol','aviatrix-systems:aviatrix-copilot:avx-cplt-byol-01','aviatrix-systems:aviatrix-copilot:avx-cplt-byol-02','aviatrix-systems:aviatrix-companion-gateway-v9:aviatrix-companion-gateway-v9','aviatrix-systems:aviatrix-companion-gateway-v10:aviatrix-companion-gateway-v10','aviatrix-systems:aviatrix-companion-gateway-v10:aviatrix-companion-gateway-v10u','aviatrix-systems:aviatrix-companion-gateway-v12:aviatrix-companion-gateway-v12','aviatrix-systems:aviatrix-companion-gateway-v13:aviatrix-companion-gateway-v13','aviatrix-systems:aviatrix-companion-gateway-v13:aviatrix-companion-gateway-v13u','aviatrix-systems:aviatrix-companion-gateway-v14:aviatrix-companion-gateway-v14','aviatrix-systems:aviatrix-companion-gateway-v14:aviatrix-companion-gateway-v14u','aviatrix-systems:aviatrix-companion-gateway-v16:aviatrix-companion-gateway-v16','canonical:0001-com-ubuntu-pro-jammy:pro-22_04-lts','center-for-internet-security-inc:cis-rhel:cis-redhat7-l1-gen1','center-for-internet-security-inc:cis-rhel-7-v2-2-0-l1:cis-rhel7-l1','center-for-internet-security-inc:cis-rhel-7-stig:cis-rhel-7-stig','center-for-internet-security-inc:cis-rhel-7-l2:cis-rhel7-l2','center-for-internet-security-inc:cis-rhel-8-stig:cis-rhel-8-stig','center-for-internet-security-inc:cis-oracle:cis-oraclelinux8-l1-gen1','center-for-internet-security-inc:cis-oracle-linux-8-l1:cis-oracle8-l1','center-for-internet-security-inc:cis-ubuntu:cis-ubuntu1804-l1','center-for-internet-security-inc:cis-ubuntu-linux-1804-l1:cis-ubuntu1804-l1','center-for-internet-security-inc:cis-ubuntu-linux-2004-l1:cis-ubuntu2004-l1','center-for-internet-security-inc:cis-ubuntu-linux-2204-l1:cis-ubuntu-linux-2204-l1-gen2','cloud-infrastructure-services:dns-ubuntu-2004:dns-ubuntu-2004','cloud-infrastructure-services:gitlab-ce-ubuntu20-04:gitlab-ce-ubuntu-20-04','cloud-infrastructure-services:squid-ubuntu-2004:squid-ubuntu-2004','cloud-infrastructure-services:load-balancer-nginx:load-balancer-nginx','cloudera:cloudera-centos-os:7_5','cncf-upstream:capi:ubuntu-1804-gen1','cncf-upstream:capi:ubuntu-2004-gen1','cncf-upstream:capi:ubuntu-2204-gen1','credativ:debian:8','credativ:debian:9','credativ:debian:9-backports','debian:debian-10:10','debian:debian-10:10-gen2','debian:debian-10:10-backports','debian:debian-10:10-backports-gen2','debian:debian-10-daily:10','debian:debian-10-daily:10-gen2','debian:debian-10-daily:10-backports','debian:debian-10-daily:10-backports-gen2','debian:debian-11:11','debian:debian-11:11-gen2','debian:debian-11:11-backports','debian:debian-11:11-backports-gen2','debian:debian-11-daily:11','debian:debian-11-daily:11-gen2','debian:debian-11-daily:11-backports','debian:debian-11-daily:11-backports-gen2','erockyenterprisesoftwarefoundationinc1653071250513:rockylinux:free','erockyenterprisesoftwarefoundationinc1653071250513:rockylinux-9:rockylinux-9','github:github-enterprise:github-enterprise','matillion:matillion:matillion-etl-for-snowflake','microsoft-dsvm:aml-workstation:ubuntu','microsoft-dsvm:ubuntu-1804:1804-gen2','microsoft-dsvm:ubuntu-2004:2004','microsoft-dsvm:ubuntu-2004:2004-gen2','netapp:netapp-oncommand-cloud-manager:occm-byol','nginxinc:nginx-plus-ent-v1:nginx-plus-ent-centos7','ntegralinc1586961136942:ntg_oracle_8_7:ntg_oracle_8_7','ntegralinc1586961136942:ntg_ubuntu_20_04_lts:ntg_ubuntu_20_04_lts','openlogic:centos-hpc:7.1','openlogic:centos-hpc:7.3','oracle:oracle-linux:8','oracle:oracle-linux:8-ci','oracle:oracle-linux:81','oracle:oracle-linux:81-ci','oracle:oracle-linux:81-gen2','oracle:oracle-linux:ol82','oracle:oracle-linux:ol8_2-gen2','oracle:oracle-linux:ol82-gen2','oracle:oracle-linux:ol83-lvm','oracle:oracle-linux:ol83-lvm-gen2','oracle:oracle-linux:ol84-lvm','oracle:oracle-linux:ol84-lvm-gen2','procomputers:almalinux-8-7:almalinux-8-7','procomputers:rhel-8-2:rhel-8-2','procomputers:rhel-8-8-gen2:rhel-8-8-gen2','procomputers:rhel-8-9-gen2:rhel-8-9-gen2','rapid7:nexpose-scan-engine:nexpose-scan-engine','rapid7:rapid7-vm-console:rapid7-vm-console','redhat:rhel:89-gen2','redhat:rhel-byos:rhel-raw76','redhat:rhel-byos:rhel-lvm88','redhat:rhel-byos:rhel-lvm88-gen2','redhat:rhel-byos:rhel-lvm92','redhat:rhel-byos:rhel-lvm-92-gen2','redhat:rhel-ha:9_2','redhat:rhel-ha:9_2-gen2','redhat:rhel-sap-apps:9_0','redhat:rhel-sap-apps:90sapapps-gen2','redhat:rhel-sap-apps:9_2','redhat:rhel-sap-apps:92sapapps-gen2','redhat:rhel-sap-ha:9_2','redhat:rhel-sap-ha:92sapha-gen2','openlogic:centos-ci:7-ci','openlogic:centos-lvm:7-lvm-gen2','oracle:oracle-database:oracle_db_21','oracle:oracle-database-19-3:oracle-database-19-0904','redhat:rhel-sap-ha:90sapha-gen2','suse:sles:12-sp4-gen2','suse:sles-15-sp2-basic:gen2','suse:sles-15-sp2-hpc:gen2','suse:sles-15-sp4-sapcal:gen1','suse:sles-byos:12-sp4','suse:sles-byos:12-sp4-gen2','suse:sles-sap:12-sp4','suse:sles-sap:12-sp4-gen2','suse:sles-sap-byos:12-sp4','suse:sles-sap-byos:12-sp4-gen2','suse:sles-sap-byos:gen2-12-sp4','suse:sles-sapcal:12-sp3','suse:sles-standard:12-sp4-gen2','suse:sles-sap-15-sp1-byos:gen1','suse:sles-sap-15-sp2-byos:gen2','talend:talend_re_image:tlnd_re','tenable:tenablecorewas:tenablecoreol8wasbyol','tenable:tenablecorenessus:tenablecorenessusbyol','thorntechnologiesllc:sftpgateway:sftpgateway','zscaler:zscaler-private-access:zpa-con-azure','cloudrichness:rockey_linux_image:rockylinux86','ntegralinc1586961136942:ntg_cbl_mariner_2:ntg_cbl_mariner_2_gen2','openvpn:openvpnas:access_server_byol','suse:sles:12-sp3','suse:sles-15-sp1-basic:gen1','suse:sles-15-sp2-basic:gen1','suse:sles-15-sp3-basic:gen1','suse:sles-15-sp3-basic:gen2','suse:sles-15-sp4-basic:gen2','suse:sles-sap:12-sp3','suse:sles-sap:15','suse:sles-sap:gen2-15','suse:sles-sap-byos:15') or imageRef matches regex 'almalinux:almalinux:8-gen.*|almalinux:almalinux-hpc:8-hpc-gen.*|almalinux:almalinux-hpc:8_5-hpc.*|almalinux:almalinux-hpc:8_7-hpc-gen.*|almalinux:almalinux:9-gen.*|almalinux:almalinux-x86_64:8-gen.*|almalinux:almalinux-x86_64:9-gen.*|canonical:.*:.*|center-for-internet-security-inc:cis-rhel:cis-redhat8-l.*-gen1|center-for-internet-security-inc:cis-rhel:cis-redhat9-l1-gen.*|center-for-internet-security-inc:cis-rhel-8-l.*:cis-rhel8-l.*|center-for-internet-security-inc:cis-rhel9-l1:cis-rhel9-l1.*|center-for-internet-security-inc:cis-oracle:cis-oraclelinux9-l1-gen.*|center-for-internet-security-inc:cis-ubuntu:cis-ubuntulinux2204-l1-gen.*|microsoftsqlserver:.*:.*|openlogic:centos:7.*|oracle:oracle-database-.*:18..*|oracle:oracle-linux:7.*|openlogic:centos:8.*|oracle:oracle-linux:ol7.*|oracle:oracle-linux:ol8.*|oracle:oracle-linux:ol9.*|redhat:rhel:7.*|redhat:rhel:8.*|redhat:rhel:9.*|redhat:rhel-byos:rhel-lvm7.*|redhat:rhel-byos:rhel-lvm8.*|redhat:rhel-ha:8.*|redhat:rhel-raw:7.*|redhat:rhel-raw:8.*|redhat:rhel-raw:9.*|redhat:rhel-sap:7.*|redhat:rhel-sap-apps:7.*|redhat:rhel-sap-apps:8.*|redhat:rhel-sap-.*:9_0|redhat:rhel-sap-ha:7.*|redhat:rhel-sap-ha:8.*|suse:opensuse-leap-15-.*:gen.*|suse:sles-12-sp5-.*:gen.*|oracle:oracle-linux:ol9-lvm.*|suse:sles-sap-12-sp5.*:gen.*|suse:sles-sap-15-.*:gen.*|suse:sle-hpc-15-sp4:gen.*|suse:sles-15-sp1-sapcal:gen.*|suse:sles-15-sp3-sapcal:gen.*|suse:sles-15-sp4:gen.*|suse:sles-15-sp4-basic:gen.*|suse:sle-hpc-15-sp4-byos:gen.*|suse:sle-hpc-15-sp5-byos:gen.*|suse:sle-hpc-15-sp5:gen.*|suse:sles-15-sp4-byos:gen.*|suse:sles-15-sp4-chost-byos:gen.*|suse:sles-15-sp4-hardened-byos:gen.*|suse:sles-15-sp5-basic:gen.*|suse:sles-15-sp5-byos:gen.*|suse:sles-15-sp5-chost-byos:gen.*|suse:sles-15-sp5-hardened-byos:gen.*|suse:sles-15-sp5-sapcal:gen.*|suse:sles-15-sp5:gen.*|suse:sles-sap-15-sp4-byos:gen.*|suse:sles-sap-15-sp4-hardened-byos:gen.*|suse:sles-sap-15-sp5-byos:gen.*|suse:sles-sap-15-sp5-hardened-byos:gen.*')))
        | extend imageRef = iff (isMarketplace, imageRef, "")
        | extend publisher = iff(isnotempty(properties.storageProfile.imageReference.publisher), properties.storageProfile.imageReference.publisher, "-")
        | extend offer = iff(isnotempty(properties.storageProfile.imageReference.offer), properties.storageProfile.imageReference.offer, "-")
        | extend plan = iff(isnotempty(properties.storageProfile.imageReference.sku), properties.storageProfile.imageReference.sku, "-")
        | project id, joinId = tolower(id), subscriptionId, type, name, machineProperties=properties, os, conf, periodicAssessment, status, resourceGroup, location, tags, imageRef, isNotInCRPAllowList, publisher, offer, plan, hotpatchStatus, kind)
        | union (resources
        | where type =~ "microsoft.hybridcompute/machines"
        | where properties.osName in~ ('Linux','Windows') or properties.osType in~ ('Linux','Windows')
        | extend os = tolower(coalesce(properties.osName, properties.osType))
        | extend assessMode = iff(os == "windows", tostring(properties.osProfile.windowsConfiguration.patchSettings.assessmentMode), tostring(properties.osProfile.linuxConfiguration.patchSettings.assessmentMode))
        | extend periodicAssessment = iff(assessMode =~ "AutomaticByPlatform", "Yes", "No")
        | extend targetVersion = "10.0.26100.0"
        | extend isHotpatchCapable = case((os in~ ('windows') and parse_version(tostring(properties.osVersion)) >= parse_version(targetVersion) and properties.osEdition in~ ('serverstandard','serverdatacenter','serverdatacentereval','serverstandardeval','serverdatacentercore','serverstandardcore')),"Not Enrolled","Not Available")
        | extend hotpatchEnablementStatus = iff(os =~ "windows", properties.osProfile.windowsConfiguration.patchSettings.status.hotpatchEnablementStatus, properties.osProfile.linuxConfiguration.patchSettings.status.hotpatchEnablementStatus)
        | extend productFeatures = (properties.licenseProfile.productProfile.productFeatures)
        | mv-expand productFeatures
        | extend IsHotpatchRow = case(productFeatures.name == "Hotpatch" and productFeatures.subscriptionStatus == "Enabled", 1, productFeatures.name == "Hotpatch" and productFeatures.subscriptionStatus == "Disabled", 2, productFeatures.name == "Hotpatch" and (productFeatures.subscriptionStatus == "Enabling" or productFeatures.subscriptionStatus == "Disabling"), 3, 0 )
        | summarize IsHotpatchEnabled = max(IsHotpatchRow) by id, subscriptionId, type, kind, name, tostring(properties), os, periodicAssessment, resourceGroup, location, tostring(tags), tostring(hotpatchEnablementStatus), tostring(isHotpatchCapable)
        | extend properties = parse_json(properties)
        | extend tags = parse_json(tags)
        | extend licenseStatus = case(IsHotpatchEnabled == 1, "Enabled", IsHotpatchEnabled == 2, "Disabled", IsHotpatchEnabled == 3, "Pending", "NoLicenseFound")
        | extend hotpatchStatusInitial = case(licenseStatus =~ "Enabled" and hotpatchEnablementStatus =~ "Enabled", "Enabled", licenseStatus =~ "Enabled" and hotpatchEnablementStatus =~ "Disabled", "Disabled", licenseStatus =~ "Enabled" and hotpatchEnablementStatus =~ "PendingEvaluation", "Pending", licenseStatus =~ "Enabled" and hotpatchEnablementStatus =~ "ActionRequired", "Action Required", licenseStatus =~ "Disabled", "Canceled", licenseStatus =~ "Enabling" or licenseStatus =~ "Disabling", "Pending","")
        | extend hotpatchStatus = iff(hotpatchStatusInitial == "",isHotpatchCapable, hotpatchStatusInitial)
        | extend hotpatchStatus = iff(isempty(hotpatchEnablementStatus) and licenseStatus =~ "Enabled", "Disabled", hotpatchStatus)
        | extend status=tostring(properties.status)
        | project id, joinId = tolower(id), subscriptionId, type, name, machineProperties=properties, os, conf = "", periodicAssessment, status, resourceGroup, location, tags, imageRef = "N/A", isNotInCRPAllowList = false, publisher = "-", offer = "-", plan = "-", hotpatchStatus, kind))
        | join kind = leftouter(
        resources
        | where type in~ ("Microsoft.SqlVirtualMachine/sqlVirtualMachines", "microsoft.azurearcdata/sqlserverinstances")
        | project resourceId = iff(type =~ "Microsoft.SqlVirtualMachine/sqlVirtualMachines", tolower(properties.virtualMachineResourceId), tolower(properties.containerResourceId)), sqlType = type
        | summarize by resourceId, sqlType
        ) on $left.joinId == $right.resourceId
        | extend type = iff(isnotempty(sqlType), sqlType, type)
        | project-away resourceId, sqlType
        | where type in~ ('microsoft.compute/virtualmachines','microsoft.hybridcompute/machines','microsoft.sqlvirtualmachine/sqlvirtualmachines', 'microsoft.azurearcdata/sqlserverinstances')
        | join kind=leftouter(
        resources
        | where type =~ "microsoft.hybridcompute/machines/licenseProfiles"
        | extend machineId = tolower(tostring(trim_end(@"/w+/(w|.)+", id)))
        | extend licenseId = tolower(tostring(properties.esuProfile.assignedLicense))
        ) on $left.joinId == $right.machineId
        | join kind=leftouter (
        resources
        | where type =~ "microsoft.hybridcompute/licenses"
        | extend licenseId = tolower(id)
        | extend licenseProps = properties
        ) on licenseId
        | extend esuStatus = case(
        (machineProperties.licenseProfile.esuProfile.esuEligibility !~ "Eligible"), 'N/A',
        (machineProperties.licenseProfile.esuProfile.licenseAssignmentState =~ 'Assigned' and licenseProps.licenseDetails.state =~ 'Activated') or machineProperties.licenseProfile.esuProfile.esuKeyState =~ 'Active', 'Enabled',
        (machineProperties.licenseProfile.esuProfile.licenseAssignmentState =~ 'NotAssigned' or licenseProps.licenseDetails.state =~ 'Deactivated') and machineProperties.licenseProfile.esuProfile.esuKeyState =~ 'Inactive', 'Not Enabled',
        'Unknown'
        )
        | join kind=leftouter ((patchassessmentresources  // resources filters i.e resource-group or location
        | where type in~ ("microsoft.compute/virtualmachines/patchassessmentresults", "microsoft.hybridcompute/machines/patchassessmentresults")
        | where properties.status =~ "Succeeded" or properties.status =~ "Inprogress" or (isnotnull(properties.configurationStatus.vmGuestPatchReadiness.detectedVMGuestPatchSupportState) and (properties.configurationStatus.vmGuestPatchReadiness.detectedVMGuestPatchSupportState =~ "Unsupported"))
        | parse id with resourceId "/patchAssessmentResults" *
        | extend resourceId=tolower(resourceId)
        | project resourceId, assessmentDataProperties=properties)) on $left.joinId == $right.resourceId
        | extend isUnsupported = isNotInCRPAllowList or (isnotnull(assessmentDataProperties.configurationStatus.vmGuestPatchReadiness.detectedVMGuestPatchSupportState) and (assessmentDataProperties.configurationStatus.vmGuestPatchReadiness.detectedVMGuestPatchSupportState =~ "Unsupported"))
        | extend patchOrchestration =
            iff(
                conf == "AutomaticByOS", "Windows Automatic Update",
                iff(
                    conf == "AutomaticByPlatformWithUserManagedSchedules", "Customer Managed Schedules",
                    iff(
                        conf == "AutomaticByPlatformUsingAutoGuestPatching", "Azure Managed - Safe Deployment",
                        iff(
                            conf == "ImageDefault", "Image Default",
                            iff(
                                conf == "Manual", "Manual",
                                "N/A"
                            )
                        )
                    )
                )
            )
        | extend hotpatchStatus = iff(isnull(assessmentDataProperties) and hotpatchStatus != "Not Available" and type =~ "microsoft.compute/virtualmachines", "Pending Evaluation", hotpatchStatus)
        | order by tolower(tostring(name)) asc
        | project resourceId=id, subscriptionId, resourceGroup, resourceType=type, resourceName=name, operatingSystem=os, location, tags, imageRef, machineProperties, patchOrchestration, periodicAssessment, vMStatus=status,  isUnsupported, assessmentDataProperties, esuStatus, publisher, offer, plan, hotpatchStatus
        ''',
        subscriptions=[]
    )

query2 = QueryRequest(
        query=f'''
          resources
        | extend joinId = tolower(id)
        | extend azureOs = tostring(properties.storageProfile.osDisk.osType)
        | extend arcOs = coalesce(tostring(properties.osName), tostring(properties.osType))
        | extend os = coalesce(azureOs, arcOs)
        | extend osType = iff(os =~ "Windows", "Windows", "Linux")
        | join kind=leftouter( resources
            | where type in~ ("Microsoft.SqlVirtualMachine/sqlVirtualMachines", "microsoft.azurearcdata/sqlserverinstances")
            | project resourceId = iff(type =~ "Microsoft.SqlVirtualMachine/sqlVirtualMachines", tolower(properties.virtualMachineResourceId), tolower(properties.containerResourceId)), sqlType = type
            | summarize by resourceId, sqlType
        ) on $left.joinId == $right.resourceId
        | extend type = iff(isnotempty(sqlType), sqlType, type)
        | project-away sqlType, resourceId
        | join kind = leftouter
        (
        patchassessmentresources
        | where type in~ ("microsoft.compute/virtualmachines/patchassessmentresults/softwarePatches", "microsoft.hybridcompute/machines/patchassessmentresults/softwarePatches")
        | parse id with resourceId "/patchAssessmentResults" *
        | extend joinId = tolower(resourceId)
        | extend uniquePatchNameWithVersion = iff(isnull(properties.kbId), strcat(tostring(properties.patchName), '_', tostring(properties.version)), properties.patchName)
        | extend publishedDateTime = iff(isnotnull(properties.publishedDateTime), properties.publishedDateTime, "N/A")
        | extend rebootRequired = iff(isnotnull(properties.rebootBehavior), properties.rebootBehavior, "N/A")
        | extend classification = iff(properties.classifications[0] =~ "UpdateRollUp", "UpdateRollup", iff(isempty(properties.classifications[0]), "Unsupported", properties.classifications[0]))
        | extend msrcSeverity = iff(isnotnull(properties.msrcSeverity), properties.msrcSeverity, "NotAvailable")
        | extend classificationPriority = iff(classification contains "Security", 0, (iff(classification == "Critical" , 1, 2)))
        | project joinId, assessProperties = properties, publishedDateTime, rebootRequired, classification, msrcSeverity, classificationPriority) on $left.joinId == $right.joinId
        | where isnotnull(assessProperties)
        | extend osUpdateClassification = iff(osType =~ "Linux", strcat("linux", tolower(classification)), tolower(classification))
        //Count will indicate the number of machines with said update pending across selected subscription(s)
        | summarize count() by publishedDateTime, resourceId = joinId, tostring(assessProperties.patchId), tostring(assessProperties.patchName), tostring(assessProperties.version), tostring(assessProperties.kbId), rebootRequired, osType, tostring(classification), msrcSeverity, classificationPriority
        ''',
        subscriptions=[]
    )


# Function to execute query
def execute_query(query):
    response = resourcegraph_client.resources(query)
    #return response.json()["data"]
    return response.data
    

# Main function
def main():
    # Execute queries
    results1 = execute_query(query1)
    results2 = execute_query(query2)

    # Convert results to DataFrames
    df1 = pd.DataFrame(results1)
    df2 = pd.DataFrame(results2)

    # Perform join on 'resourceid'
    merged_df = pd.merge(df1, df2, on='resourceId', how='left',validate='1:m')

    # Display the merged results
    print(merged_df)

    # 导出合并的结果为CSV文件
    df1.to_csv('df1.csv', index=False)
    df2.to_csv('df2.csv', index=False)
    merged_df.to_csv('merged_results.csv', index=False)


if __name__ == '__main__':
    main()