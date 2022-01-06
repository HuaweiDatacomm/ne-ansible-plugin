#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# This file is part of Ansible
#
# Ansible is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Ansible is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Ansible.  If not, see <http://www.gnu.org/licenses/>.
#

ANSIBLE_METADATA = {'metadata_version': '1.1',
                    'status': ['preview'],
                    'supported_by': 'community'}

DOCUMENTATION = """
---
module: ne_facts
version_added: "2.6"
author: "wangdezhuang (@QijunPan)"
short_description: Gets facts about HUAWEI NetEngine routers.
description:
  - Collects facts from CloudEngine devices running the NetEngine
    operating system.  Fact collection is supported over Netconf
    transport.  This module prepends all of the base network fact keys
    with C(ansible_net_<fact>).  The facts module will always collect a
    base set of facts from the device and can enable or disable
    collection of additional facts.
options:
  gather_subset:
    description:
      - When supplied, this argument will restrict the facts collected
        to a given subset.  Possible values for this argument include
        all, hardware, lldpneighbors, and interfaces.  Can specify a
        list of values to include a larger subset.  Values can also be used
        with an initial C(M(!)) to specify that a specific subset should
        not be collected.
    required: false
    default: '!hardware'
"""

EXAMPLES = """
# Note: examples below use the following provider dict to handle
#       transport and authentication to the node.
---
- name: ne_facts
  hosts: ne_test
  connection: netconf
  gather_facts: no
  vars:
    netconf:
      host: "{{ inventory_hostname }}"
      port: "{{ ansible_ssh_port }}"
      username: "{{ ansible_user }}"
      password: "{{ ansible_ssh_pass }}"
      transport: netconf
  tasks:
  - name: "Gather_subset is all"
    ne_facts:
      gather_subset: all
      provider: "{{ netconf }}"
  - name: "Collect only the hardware facts"
    ne_facts:
      gather_subset: hardware
      provider: "{{ netconf }}"
  - name: "Do not collect hardware facts"
    ne_facts:
      gather_subset: "!hardware"
      provider: "{{ netconf }}"
"""

RETURN = """
gather_subset:
  description: The list of fact subsets collected from the device
  returned: always
  type: list
# default
System Info:
  description: The major system information on the remote device
  returned: always
  type: dict
  sys-name:
      description: System name.
      returned: always
      type: str
  sys-contact:
      description: System contact information.
      returned: always
      type: str
  sys-location:
      description: System location information.
      returned: always
      type: str
  sys-desc:
      description: Textual description of an entity.
      returned: always
      type: str
  sys-object-id:
      description: Entity OID.
      returned: always
      type: str
  system-gmt-time:
      description: Current system time in UTC seconds.
      returned: always
      type: str
  sys-uptime:
      description: Time elapses since the system is running.
      returned: always
      type: str
  sys-service:
      description: Integer value which indicates the set of services that this entity offers.
      returned: always
      type: str
  platform-name:
      description: Name of a platform. For example, Huawei Versatile Routing Platform.
      returned: always
      type: str
  platform-version:
      description: Version of a platform. For example, VRP (R) Software, Version 8.10.
      returned: always
      type: str
  product-name:
      description: Name of a product. For example, Quidway NetEngine 5000E.
      returned: always
      type: str
  product-version:
      description: Product version. The version format is VxxRxxCxxSPxxx, for example, V800R002C01SPC001.
      returned: always
      type: str
  patch-version:
      description: Latest patch version. The version format is CPxxx/HPxxx, for example, CP001.
      returned: always
      type: str
  esn:
      description: Product ESN number.
      returned: always
      type: str
  mac:
      description: System MAC address.
      returned: always
      type: str
Licence Info:
    description: Proof of permission granted.
    returned: always
    type: dict
  LicenceItem:
      description: All license items.
      returned: always
      type: dict
    name:
        description: License item name.
        returned: always
        type: str
    description:
        description: The description of a license item.
        returned: always
        type: str
    default-value:
        description: The default value of a license item.
        returned: always
        type: str
    ...
  LicenceFileInfo:
      description: All information of a license file.
      returned: always
      type: dict
    filename:
        description: The name of a license file.
        returned: always
        type: str
    filesize:
        description: The size of a license file.
        returned: always
        type: str
    generalInfo:
        description: The general information of a license file.
        returned: always
        type: dict
      serial-number:
          description: The serial number of a license file.
          returned: always
          type: str
      creator:
          description: The creator of a license file.
          returned: always
          type: str
      created-time:
          description: The created time of a license file.
          returned: always
          type: str
      ...
#hardware
CPU:
  description: CPU information of boards.
  returned: when hardware is configured
  type: dict
  index:
      description: Board index.
      returned: when hardware is configured
      type: str
  system-cpu-usage:
      description: CPU usage.
      returned: when hardware is configured
      type: str
  overload-threshold:
      description: Overload threshold.
      returned: when hardware is configured
      type: str
  unoverload-threshold:
      description: Overload alarm clear threshold.
      returned: when hardware is configured
      type: str
  current-overload-state:
      description: Current overload state.
      returned: when hardware is configured
      type: str
Memory:
  description: Memory information of boards.
  returned: when hardware is configured
  type: dict
  index:
      description: Board index.
      returned: when hardware is configured
      type: str
  os-memory-total:
      description: Total OS memory.
      returned: when hardware is configured
      type: str
  os-memory-free:
      description: Available OS memory.
      returned: when hardware is configured
      type: str
  os-memory-usage:
      description: OS memory usage.
      returned: when hardware is configured
      type: str
  overload-threshold:
      description: Overload threshold.
      returned: when hardware is configured
      type: str
  unoverload-threshold:
      description: Overload alarm clear threshold.
      returned: when hardware is configured
      type: str
  current-overload-state:
      description: Current overload state.
      returned: when hardware is configured
      type: str
System available files:
    description: Specify system available file information.It will be displayed by name, attributes, modification time, and file size
    returned: when hardware is configured
    type: dict
phyEntity:
    description: Information about a physical entity.It include chassis, container, Module(lpuModule, sfuModule, cmuModule, cfModule, flexibleCardModule), fan, powerSupply, port informatinos.
    returned: when hardware is configured
    type: dict
    class:
        description: Entity class.
        returned: when hardware is configured
        type: str
    position:
        description: Entity position.
        returned: when hardware is configured
        type: str
    serial-number:
        description: Entity number.
        returned: when hardware is configured
        type: str
    index:
        description: Entity index.
        returned: when hardware is configured
        type: str:
    chassis-index:
        description: Chassis index.
        returned: when hardware is configured
        type: str:
     ...
 #Interfaces
Ipv4 Addr:
  description: All IPv4 addresses configured on the device
  returned: when interfaces is configured
  type: dict
  ip:
      description: IPv4 address.
      returned: when interfaces is configured
      type: str
  netmask:
      description: IPv4 address mask.
      returned: when interfaces is configured
      type: str
  type:
      description: IPv4 address type.
      returned: when interfaces is configured
      type: str
Ipv6 Addr:
  description: All IPv6 addresses configured on the device
  returned: when interfaces is configured
  type: dict
  ip:
      description: IPv6 address.
      returned: when interfaces is configured
      type: str
  prefix-length:
      description: Length of the IPv6 address prefix.
      returned: when interfaces is configured
      type: str
  type:
      description: IPv6 address type.
      returned: when interfaces is configured
      type: str
  algorithm-type:
      description: Address algorithm type.
      returned: when interfaces is configured
      type: str
#lldpneighbors
lldoNeighbors Info
    description: The list of LLDP neighbors from the remote device.
    returned: when lldoneighbors is configured
    type: str
    index:
        description: Neighbor index.
        returned: when lldoneighbors is configured
        type: str
    chassis-id-sub-type:
        description: Chassis type.
        returned: when lldoneighbors is configured
        type: str
    chassis-id:
        description: Chassis ID.
        returned: when lldoneighbors is configured
        type: str
    port-id-sub-type:
        description: Interface ID subtype.
        returned: when lldoneighbors is configured
        type: str
    port-id:
        description: Interface ID.
        returned: when lldoneighbors is configured
        type: str
    system-name:
        description: System name.
        returned: when lldoneighbors is configured
        type: str
    expired-time:
        description: Expired time.
        returned: when lldoneighbors is configured
        type: str
"""

import re
import sys
from ansible_collections.huaweidatacom.ne.plugins.module_utils.network.ne.ne import get_nc_config
from ansible_collections.huaweidatacom.ne.plugins.module_utils.network.ne.ne import ne_argument_spec, check_args
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.six import iteritems
if sys.version_info.major != 2:
    import importlib
    importlib.reload(sys)
else:
    reload(sys)
    sys.setdefaultencoding('utf-8')

try:
    from lxml.etree import Element, SubElement, tostring, fromstring
except ImportError:
    from xml.etree.ElementTree import Element, SubElement, tostring, fromstring

try:
    from lxml.etree import ParseError
except ImportError:
    try:
        from xml.etree.ElementTree import ParseError
    except ImportError:
        from xml.parsers.expat import ExpatError
        ParseError = ExpatError


class FactsBase(object):

    STR_XML = frozenset()

    def __init__(self, module):
        self.module = module
        self.facts = dict()
        self.responses = []

    def populate(self):
        for XML in self.STR_XML:
            if XML:
                module_names = re.findall('"urn:huawei:yang:(.*)"', XML)
                xml_response = get_nc_config(self.module, XML)
                xml_response_stripping = self.__stripping(xml_response, module_names)
                self.responses.append(xml_response_stripping)

    def __stripping(self, xml_str,module_names):
        if xml_str:
            xml_str = xml_str.replace('\r', '').replace('\n', '').replace(
                ' xmlns="urn:ietf:params:xml:ns:netconf:base:1.0"', '')
            if module_names:
                for module_name in module_names:
                    xml_str = xml_str.replace(' xmlns="urn:huawei:yang"', '').replace(
                ' xmlns="urn:huawei:yang:%s"' % module_name, '')
        return xml_str

    def dict_delelement(self, dict, list):
        for item in list:
            del dict[item]
        return dict



class Default(FactsBase):
    """ Class default """
    CURRENT_CONFIGURATION_SYSNAME_XML = """
<filter type="subtree">
  <system:system xmlns:system="urn:huawei:yang:huawei-system">
    <system:system-info/>
  </system:system>
</filter>
"""
    LICENCE_XML = """
<filter type="subtree">
  <license:license xmlns:license="urn:huawei:yang:huawei-license">
    <license:license-items/>
    <license:license-files/>
  </license:license>
</filter>
"""
    STR_XML = [CURRENT_CONFIGURATION_SYSNAME_XML, LICENCE_XML]

    def populate(self):
        """ Populate method """

        super(Default, self).populate()

        xml_str = self.responses[0]
        self.facts['Default:System Info'] = self.parse_sysname(xml_str)

        xml_str = self.responses[1]
        self.facts['Default:Licence Info'] = self.parse_licence(xml_str)
    def parse_sysname(self, xml_str):
        """ Parse sysname method """

        sysinfo_dict = dict()
        if xml_str:
            root = fromstring(xml_str.encode('utf-8'))
            systeminfo = root.xpath("//system-info/*")
            for systeminfo_item in systeminfo:
                sysinfo_dict[systeminfo_item.tag] = systeminfo_item.text
        return sysinfo_dict

    def parse_licence(self, xml_str):
        """ Parse licence method """

        licence_dict = dict()
        lcsitem_dict = dict()
        lcsfile_dict = dict()
        if xml_str:
            root = fromstring(xml_str.encode('utf-8'))
            """lcsItem part"""
            lcsitem = root.xpath("//license-item")
            creatVar = locals()
            for lcsitem_item in lcsitem:
                lcsitemname = lcsitem_item.xpath("./name")[0].text
                creatVar[lcsitemname] = {}
                lcsitem_var = creatVar.get(lcsitemname)
                for item in lcsitem_item.xpath("./*"):
                    if (item.text == '--'):
                        lcsitem_var[item.tag] = 'not Support'
                    else:
                        lcsitem_var[item.tag] = item.text
                lcsitem_dict[lcsitemname] = lcsitem_var
            licence_dict['LicenceItem'] = lcsitem_dict
            """lcsfileinfo part"""
            lcsfile = root.xpath("//license-file")
            if lcsfile:
                lcsfile = lcsfile[0]
                lcsfile_dict['fileName'] = lcsfile.xpath("./filename")[0].text
                lcsfile_dict['licenseFileSize'] = lcsfile.xpath("./filesize")[0].text + 'Kb'
                lcsfile_dict['generalInfo'] = dict()
                for item in lcsfile.xpath("./general/*"):
                    lcsfile_dict['generalInfo'][item.tag] = item.text
            licence_dict['LicenceFileInfo'] = lcsfile_dict
        return licence_dict


class LldpNeighbors(FactsBase):
    """ Class LldpNeighbors """
    LLDPNEIGHBORS_XML = """
<filter type="subtree">
  <ifm:ifm xmlns:ifm="urn:huawei:yang:huawei-ifm"
           xmlns:lldp="urn:huawei:yang:huawei-lldp">
    <ifm:interfaces>
      <ifm:interface>
        <ifm:name/>
        <lldp:lldp>
          <lldp:session>
            <lldp:neighbors>
              <lldp:neighbor>
                <lldp:index/>
                <lldp:chassis-id-sub-type/>
                <lldp:chassis-id/>
                <lldp:port-id-sub-type/>
                <lldp:port-id/>
                <lldp:system-name/>
                <lldp:expired-time/>
              </lldp:neighbor>
            </lldp:neighbors>
          </lldp:session>
        </lldp:lldp>
      </ifm:interface>
    </ifm:interfaces>
  </ifm:ifm>
</filter>
"""
    STR_XML = [LLDPNEIGHBORS_XML]

    def populate(self):
        """ Populate method """

        super(LldpNeighbors, self).populate()

        xml_str = self.responses[0]
        self.facts['LLDP:lldpNeighbors Info'] = self.parse_lldpneighbor(xml_str)

    def parse_lldpneighbor(self, xml_str):
        """ Parse lldpneighbor method """
        lldp_dict = dict()
        if xml_str:
            root = fromstring(xml_str.encode('utf-8'))
            lldpinterface = root.xpath("//interface")
            creatVar = locals()
            for lldpinterface_item in lldpinterface:
                interfacename = lldpinterface_item.xpath("./name")[0].text
                lldpneighbors = lldpinterface_item.xpath("./lldp/session/neighbors/neighbor")
                creatVar[interfacename] = []
                interface_var = creatVar.get(interfacename)
                if(lldpneighbors):
                    for lldpneighbor_item in lldpneighbors:
                        item_dict = {}
                        for item in lldpneighbor_item.xpath("./*"):
                            item_dict[item.tag] = item.text
                        interface_var.append(item_dict)
                lldp_dict[interfacename] = interface_var
        return lldp_dict

class Hardware(FactsBase):
    """ Class hardware """
#     DIR_XML = """<filter type="subtree">
#   <vfm xmlns="http://www.huawei.com/netconf/vrp/huawei-vfm">
#     <dirs>
#       <dir>
#       </dir>
#     </dirs>
#   </vfm>
# </filter>"""
    DISPLAY_MEMORY_XML = """
<filter type="subtree">
  <debug:debug xmlns:debug="urn:huawei:yang:huawei-debug">
    <debug:memory-infos>
      <debug:memory-info/>
    </debug:memory-infos>
  </debug:debug>
</filter>
"""
    DISPALY_DEVICE_XML = """
<filter type="subtree">
  <devm:devm xmlns:devm="urn:huawei:yang:huawei-devm">
    <devm:physical-entitys>
      <devm:physical-entity/>
    </devm:physical-entitys>
  </devm:devm>
</filter>
"""
    DISPLAY_CPU_XML = """
<filter type="subtree">
  <debug:debug xmlns:debug="urn:huawei:yang:huawei-debug">
    <debug:cpu-infos>
      <debug:cpu-info/>
    </debug:cpu-infos>
  </debug:debug>
</filter>
"""
    STR_XML = [DISPLAY_MEMORY_XML, DISPLAY_CPU_XML, DISPALY_DEVICE_XML]

    def populate(self):
        """ Populate method """

        super(Hardware, self).populate()

        # xml_str = self.responses[0]
        # self.facts['Hardware:System available files'] = self.parse_dirs(xml_str)

        xml_str = self.responses[0]
        self.facts['Hardware:Memory'] = self.parse_memory(xml_str)

        xml_str = self.responses[1]
        self.facts['Hardware:CPU'] = self.parse_cpu(xml_str)

        xml_str = self.responses[2]
        self.facts['Hardware:phyEntity'] = self.parse_phyentity(xml_str)

    # def parse_dirs(self, xml_str):
    #     """ Parse dirs method """
    #
    #     dir_dict = dict()
    #     if xml_str:
    #         root = fromstring(xml_str.encode('utf-8'))
    #         dirs = root.xpath("//dir")
    #         if dirs:
    #             for dir_item in dirs:
    #                 filename = dir_item.xpath("fileName")[0].text
    #                 dirname = dir_item.xpath("dirName")[0].text + filename
    #                 attr = dir_item.xpath("Attr")[0].text
    #                 modifydatatiom = dir_item.xpath("modifyDatetime")[0].text
    #                 intdirsize = dir_item.xpath("intDirSize")[0].text
    #                 dir_dict[dirname] = attr + ' ' + modifydatatiom + ' ' + intdirsize + 'Kb'
    #     return dir_dict

    def parse_memory(self, xml_str):
        """ Parse memory method """

        memory_dict = dict()
        if xml_str:
            root = fromstring(xml_str.encode('utf-8'))
            memoryinfo = root.xpath("//memory-info")
            for memoryinfo_item in memoryinfo:
                positionname = 'position ' + memoryinfo_item.xpath("./position")[0].text
                memory_dict[positionname] = {}
                memory_dict[positionname]['index'] = memoryinfo_item.xpath("index")[0].text
                memory_dict[positionname]['osMemoryTotal'] = memoryinfo_item.xpath("./os-memory-total")[0].text + 'Kb'
                memory_dict[positionname]['osMemoryFree'] = memoryinfo_item.xpath("./os-memory-free")[0].text + 'Kb'
                memory_dict[positionname]['osMemoryUsage'] = memoryinfo_item.xpath("./os-memory-usage")[0].text + '%'
                memory_dict[positionname]['ovloadThreshold'] = memoryinfo_item.xpath("./overload-threshold")[0].text + '%'
                memory_dict[positionname]['unovloadThreshold'] = memoryinfo_item.xpath("./unoverload-threshold")[0].text + '%'
                memory_dict[positionname]['currentOvloadState'] = memoryinfo_item.xpath("./current-overload-state")[0].text
        return memory_dict

    def parse_cpu(self, xml_str):
        """ Parse cpu method """

        cpu_dict = dict()
        if xml_str:
            root = fromstring(xml_str.encode('utf-8'))
            cpuinfo = root.xpath("//cpu-info")
            for cpuinfo_item in cpuinfo:
                positionname = 'position ' + cpuinfo_item.xpath("./position")[0].text
                cpu_dict[positionname] = {}
                cpu_dict[positionname]['index'] = cpuinfo_item.xpath("./index")[0].text
                cpu_dict[positionname]['systemCpuUsage'] = cpuinfo_item.xpath("./system-cpu-usage")[0].text + '%'
                cpu_dict[positionname]['ovloadThreshold'] = cpuinfo_item.xpath("./overload-threshold")[0].text + '%'
                cpu_dict[positionname]['unovloadThreshold'] = cpuinfo_item.xpath("./unoverload-threshold")[0].text + '%'
                cpu_dict[positionname]['currentOvloadState'] = cpuinfo_item.xpath("./current-overload-state")[0].text
        return cpu_dict

    def parse_phyentity(self, xml_str):
        """ Parse phyentity method """

        phyentity_dict = dict()
        if xml_str:
            root = fromstring(xml_str.encode('utf-8'))
            phyentity = root.xpath("//physical-entity")
            creatVar = locals()
            for phyentity_item in phyentity:
                entname = phyentity_item.xpath("./class")[0].text +  phyentity_item.xpath("./position")[0].text + '(Index:' + phyentity_item.xpath("./index")[0].text + ')'
                creatVar[entname] = dict()
                phyentity_var = creatVar.get(entname)
                for item in phyentity_item.xpath("child::*"):
                    phyentity_var[item.tag] = item.text
                phyentity_dict[entname] = phyentity_var
                phyentity_sort = self.sortphyentity(phyentity_dict)
        return phyentity_sort

    def sortphyentity(self, dicts):
        """ Sort phyEntity method """

        outdicts = dict(chassis=dict(),
                        container=dict(),
                        module=dict(),
                        port=dict(),
                        fan=dict(),
                        powerSupply=dict(),
                        other=dict()
                        )
        if dicts:
            for Kitem, Vitem in dicts.items():
                if 'chassis' in Kitem:
                    outdicts['chassis'][Kitem]= Vitem
                elif 'container' in Kitem:
                    outdicts['container'][Kitem] = Vitem
                elif 'Module' in Kitem:
                    outdicts['module'][Kitem] = Vitem
                elif 'port' in Kitem:
                    outdicts['port'][Kitem] = Vitem
                elif 'fan' in Kitem:
                    outdicts['fan'][Kitem] = Vitem
                elif 'powerSupply' in Kitem:
                    outdicts['powerSupply'][Kitem] = Vitem
                else:
                    outdicts['other'][Kitem] = Vitem
        return outdicts


class Interfaces(FactsBase):
    """ Class interfaces """

    IPV4_INTERFACES_BRIEF_XML = """
<filter type="subtree">
  <ni:network-instance xmlns:if-ip="urn:huawei:yang:huawei-if-ip"
                       xmlns:ni="urn:huawei:yang:huawei-network-instance">
    <ni:instances>
      <ni:instance>
        <if-ip:ipv4-if-states>
          <if-ip:ipv4-if-state>
            <if-ip:addresses/>
          </if-ip:ipv4-if-state>
        </if-ip:ipv4-if-states>
      </ni:instance>
    </ni:instances>
  </ni:network-instance>
</filter>
"""
    IPV6_INTERFACES_BRIEF_XML = """
<filter type="subtree">
  <ni:network-instance xmlns:if-ip="urn:huawei:yang:huawei-if-ip"
                       xmlns:ni="urn:huawei:yang:huawei-network-instance">
    <ni:instances>
      <ni:instance>
        <if-ip:ipv6-ifs>
          <if-ip:ipv6-if>
            <if-ip:addresses/>
          </if-ip:ipv6-if>
        </if-ip:ipv6-ifs>
      </ni:instance>
    </ni:instances>
  </ni:network-instance>
</filter>
"""
    STR_XML = [IPV4_INTERFACES_BRIEF_XML, IPV6_INTERFACES_BRIEF_XML]

    def populate(self):
        """ Populate method"""

        super(Interfaces, self).populate()

        xml_str = self.responses[0]
        self.facts['Interfaces:Ipv4 Addr'] = self.parse_ipv4(xml_str)

        xml_str = self.responses[1]
        self.facts['Interfaces:Ipv6 Addr'] = self.parse_ipv6(xml_str)

    def parse_ipv4(self, xml_str):
        """ Parse IPV4 method """

        ipv4_addr_dict = dict()
        if xml_str:
            root = fromstring(xml_str.encode('utf-8'))
            instance = root.xpath("//instance")
            if instance:
                creatVar = locals()
                for instance_item in instance:
                    ipv4name = instance_item.xpath("./name")[0].text
                    creatVar[ipv4name] = dict()
                    ipv4_var = creatVar.get(ipv4name)
                    ipv4addr = instance_item.xpath("./ipv4-if-states/ipv4-if-state/addresses/address")
                    for ipv4addr_item in ipv4addr:
                        for item in (ipv4addr_item.xpath("./*")):
                            ipv4_var[item.tag] = item.text
                    ipv4_addr_dict[ipv4name] = ipv4_var
        return ipv4_addr_dict

    def parse_ipv6(self, xml_str):
        """ Parse IPV6 method """

        ipv6_addr_dict = dict()
        if xml_str:
            root = fromstring(xml_str.encode('utf-8'))
            instance = root.xpath("//instance")
            if instance:
                creatVar = locals()
                for instance_item in instance:
                    ipv6name = instance_item.xpath("./name")[0].text
                    creatVar[ipv6name] = []
                    ipv6_var = creatVar.get(ipv6name)
                    ipv6addr = instance_item.xpath("./ipv6-ifs/ipv6-if/addresses/address")
                    for ipv6addr_item in ipv6addr:
                        ipv6_addr_var = dict()
                        for item in (ipv6addr_item.xpath("./*")):
                            ipv6_addr_var[item.tag] = item.text
                        ipv6_var.append(ipv6_addr_var)
                    ipv6_addr_dict[ipv6name] = ipv6_var
            return ipv6_addr_dict


FACT_SUBSETS = dict(
    default=Default,
    hardware=Hardware,
    interfaces=Interfaces,
    lldpneighbors=LldpNeighbors,
)

VALID_SUBSETS = frozenset(FACT_SUBSETS.keys())


def main():
    """ Module main """
    #pydevd.settrace('10.134.214.203', port=10016, stdoutToServer=True, stderrToServer=True)
    spec = dict(
        gather_subset=dict(default=['!lldpneighbors'], type='list')
    )
    spec.update(ne_argument_spec)

    module = AnsibleModule(argument_spec=spec, supports_check_mode=True)

    warnings = list()
    check_args(module, warnings)

    gather_subset = module.params['gather_subset']

    runable_subsets = set()
    exclude_subsets = set()

    for subset in gather_subset:
        if subset == 'all':
            runable_subsets.update(VALID_SUBSETS)
            continue
        if subset.startswith('!'):
            subset = subset[1:]
            if subset == 'all':
                exclude_subsets.update(VALID_SUBSETS)
                continue
            exclude = True
        else:
            exclude = False
        if subset not in VALID_SUBSETS:
            module.fail_json(msg='Bad subset')
        if exclude:
            exclude_subsets.add(subset)
        else:
            runable_subsets.add(subset)

    if not runable_subsets:
        runable_subsets.update(VALID_SUBSETS)

    runable_subsets.difference_update(exclude_subsets)
    runable_subsets.add('default')

    facts = dict()
    facts['gather_subset'] = list(runable_subsets)

    instances = list()
    for key in runable_subsets:
        instances.append(FACT_SUBSETS[key](module))

    for inst in instances:
        inst.populate()
        facts.update(inst.facts)

    ansible_facts = dict()
    for key, value in iteritems(facts):
        if key.startswith('_'):
            ansible_facts[key[1:]] = value
        else:
            ansible_facts[key] = value

    module.exit_json(ansible_facts=ansible_facts, warnings=warnings)


if __name__ == '__main__':
    main()
