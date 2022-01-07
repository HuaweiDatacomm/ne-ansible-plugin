#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import os
import sys
import copy
import logging
import json
from collections import OrderedDict
import hashlib
import xmltodict
from lxml import etree
from xml.dom.minidom import parseString
from ansible.module_utils.basic import AnsibleModule
from ansible.module_utils.connection import Connection, ConnectionError
from ansible_collections.huaweidatacom.ne.plugins.module_utils.network.ne.ne import get_nc_config, ne_argument_spec, get_nc_connection, to_text, to_string, execute_nc_action_yang
#from ansible.module_utils.network.ne.ne import get_nc_config, ne_argument_spec, get_nc_connection, to_text, to_string, execute_nc_action_yang
from ansible_collections.huaweidatacom.ne.plugins.module_utils.network.ne.common_module.checkparams import check_params
import xmltodict
from ansible_collections.huaweidatacom.ne.plugins.module_utils.network.ne.common_module.xml_build_with_xmlns import xml_parser_join_xmlns
from ansible.module_utils.common.yaml import yaml_load
from ansible.module_utils.common import *

try:
    from ncclient.xml_ import to_xml
    HAS_NCCLIENT = True
except ImportError:
    HAS_NCCLIENT = False

try:
    import xml.etree.cElementTree as ET
except:
    import xml.etree.ElementTree as ET

try:
    from mediator.netconf_translate import translate_edit_config_content, translate_query_filter_content
    HAS_MEDIATOR = True
except ImportError:
    HAS_MEDIATOR = False

params_default_list = {'host', 'port', 'username', 'password', 'ssh_keyfile',
                       'timeout', 'transport', 'operation_specs',
                       'provider', 'operation_type'}


class ConfigBase(object):
    """Create a ConfigBase class object"""

    def __init__(self, *args):
        self.argument_spec, self.leaf_info, self.namespaces, self.business_tag, \
        self.xml_head, self.xml_tail, self.key_list = args
        self.module = None

        # config result state
        self.changed = False
        self.updates_cmd = list()
        self.results = dict()
        self.translate_ietf = str()
        self.ietf_routing = str()
        self.proposed = dict()
        self.existing = dict()
        self.end_state = dict()

    def init_module(self):
        """ init module """
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True)
        return self.module

    def get_operation_type(self):
        """Get operation type"""
        self.init_module()
        return self.module.params

    # config_set Echo check function
    def check_response(self, xml_str):
        """Check if response message is already succeed."""
        if "<ok/>" not in xml_str:
            self.module.fail_json(msg=xml_str)
        elif " <rpc-error>" in xml_str:
            self.module.fail_json(msg=xml_str)

    def get_body_xml(self, oper):
        """Config_set construct the body part of the message."""
        params_copy = copy.deepcopy(self.module.params)
        business_params = {}
        for business in self.business_tag:
            business_params[business] = params_copy[business]
        if oper == 'config':
            new_params = {'root': business_params}
        else:
            # Remove the non-key node, otherwise the get message is incorrect.
            new_business_params = self.remove_not_key(business_params, self.key_list, "")
            new_params = {'root': new_business_params}
        body_xml = parseString(self.params_to_xml(oper, new_params)).toprettyxml()
        body_xml_list = re.compile(r"<root>(.*?)</root>", re.S).findall(body_xml)
        if not body_xml_list:
            return
        body_xml_str = body_xml_list[0]
        return body_xml_str

    def remove_not_key(self, dic, paths, spath):
        """Remove non-key nodes."""
        for k in list(dic.keys()):
            spath = spath + "/" + k
            if isinstance(dic[k], dict):
                dic[k].update(
                    self.remove_not_key(dic[k], paths, spath))
            elif isinstance(dic[k], list):
                temp_list = []
                for item in dic[k]:
                    temp_list.append(
                        self.remove_not_key(item, paths, spath))
                dic.update({k: temp_list})
            else:
                if spath in paths:
                    pass
                else:
                    if dic[k] is None:
                        del dic[k]
                    else:
                        dic[k] = None
            spath = spath[:-(len(spath.split("/")[-1]) + 1)]
        return dic

    def str_to_xml(self, cfg_str):
        """Convert the spliced string to xml."""
        cfg_str_to_doc = parseString(cfg_str).toprettyxml()
        xml_list = [line.strip() for line in cfg_str_to_doc.split("\n") if line]
        update_xml = parseString(''.join(xml_list)).toprettyxml()
        root = etree.fromstring(update_xml)
        if self.module.params.get('operation_specs', None):
            update_xml = self.create_operation_xml(self.module.params, root)
        return self.create_operation_namespace(update_xml)

    def create_operation_xml(self, node_params, root):
        """Create operation xml"""
        # Add a user-defined operation
        update_xml = ""
        for dic in node_params.get('operation_specs'):
            path = dic['path']
            operation = dic['operation']
            user_tag = root.xpath(path)
            user_tag[0].set("operation", operation)
            update_xml = parseString(etree.tostring(root)).toprettyxml(indent='\t', newl='\n')
        return update_xml

    def create_operation_namespace(self, update_xml):
        """Add a namespace to the xml file"""
        update_xml_temp = xml_parser_join_xmlns(update_xml, self.namespaces, "config")
        ret_str = update_xml_temp.replace("operation", "nc:operation")
        return ret_str

    def config_str(self):
        """Config_set message stitching"""
        cfg_str = ''
        cfg_str += self.xml_head.replace('nc:operation', 'operation')
        cfg_str += self.get_body_xml('config')
        cfg_str += self.xml_tail
        return cfg_str

    def load_json(self, xml):
        """json to xml"""
        try:
            json_str = xmltodict.parse(xml)
            json_s = json.dumps(json_str, indent=4)
            return json.loads(json_s)
        except Exception:
            print("xmltojson failed!")

    def json_to_xml(self, json):
        """xml to json"""
        xml_str = xmltodict.unparse(json, pretty='True')
        return xml_str

    def netconf_set_config(self):
        """The final config_set message is sent to the controlled machine."""
        cfg_str = self.config_str()
        xml_str = self.str_to_xml(cfg_str)
        ietf_xml_json = self.load_json(xml_str)
        self.ietf_routing = self.json_to_xml(ietf_xml_json)
        if HAS_MEDIATOR:
            xml_cfg_str = translate_edit_config_content(xml_str).replace('True', 'true'). \
                replace('False', 'false')
        else:
            xml_cfg_str = xml_str
        self.translate_ietf = xml_cfg_str
        recv_xml = self.set_nc_config_without_default_operation(self.module, xml_cfg_str)
        self.check_response(recv_xml)
        return recv_xml

    # ietf config message not need the param:<default-operation>
    # Duplicate the fun:set_nc_config
    def set_nc_config_without_default_operation(self, module, xml_str):
        """ set_config """
        conn = get_nc_connection(module)
        if xml_str is not None:
            try:
                out = conn.edit_config(target='running', config=xml_str, error_option='rollback-on-error')
            except ConnectionError as exc:
                module.fail_json(msg=to_text(exc))
            finally:
                pass
        else:
            return None
        return to_string(to_xml(out))

    def get_config_str(self):
        """config_get Message stitching"""
        get_cfg_str = ''
        replace_xml_head = self.xml_head.replace('config', 'filter type="subtree"')
        if re.compile(r' nc:operation="\w*"?'):
            new_xml_head = re.compile(r' nc:operation="\w*"?').sub('', replace_xml_head)
        else:
            new_xml_head = replace_xml_head
        get_cfg_str += new_xml_head
        get_cfg_str += self.get_body_xml('get')
        get_cfg_str += self.xml_tail.replace('config', 'filter')
        return get_cfg_str

    def params_to_xml(self, oper, params):
        """Convert params dictionary type to xml format."""
        return self.to_xml(oper, params)

    def to_xml(self, oper, params):
        """Deep traversal of the dictionary and remove the default value."""
        xml_list = []
        for key, value in params.items():
            if key not in params_default_list:
                if isinstance(value, dict):
                    xml_value = self.to_xml(oper, value)
                    xml_str = self.xml_tag(key, xml_value)
                elif isinstance(value, list):
                    xml_value = ""
                    for item in value:
                        xml_value = xml_value + self.to_xml(oper, item)
                    xml_str = self.xml_tag(key, xml_value)
                else:  # The type of value might be None/int/str/bool
                    if value is None and oper == "config":
                        continue
                    if type(value) == bool:
                        value = str(value).lower()
                    xml_str = self.xml_tag(key, value)
                xml_list.append(xml_str)
        return ''.join(xml_list)

    def xml_tag(self, key, value):
        """Generate xml format for each line"""
        xml_str = ("<%s>{value}</%s>" % (key, key)) \
            .format(key=key, value=value if value is not None else '')
        return xml_str

    def get_xml_str(self):
        """Get the xml which is get message."""
        get_cfg_str = self.get_config_str()
        cfg_str_to_doc = parseString(get_cfg_str).toxml()
        xml_list = [line.strip() for line in cfg_str_to_doc.split("\n") if line]
        get_xml = parseString(''.join(xml_list)).toprettyxml()
        get_xml_str = get_xml.replace('<?xml version="1.0" ?>', '')
        xml_str = parseString(get_xml_str).toprettyxml()
        return xml_str

    def netconf_get_config(self):
        """The final Config_get message is sent to the controlled machine."""
        xml_str = self.get_xml_str()
        update_xml_result = xml_parser_join_xmlns(xml_str, self.namespaces, 'filter')
        get_str = update_xml_result.replace('<?xml version="1.0" ?>', '')
        if HAS_MEDIATOR:
            translate_xml_str = translate_query_filter_content(get_str)
        else:
            translate_xml_str = get_str
        return self.get_info_process(translate_xml_str)

    # The config_get packet is sent to return the current configuration parameters of the device.
    def get_info_process(self, xml_str):
        """Get current dldp existed configuration"""
        conf = dict()
        # Send a Get message
        # Parsing 1: delete the useless string, pay attention to the replacement according to the business
        con_obj = get_nc_config(self.module, xml_str)

        # Parsing 2: No data detection
        if "<data/>" in con_obj:
            return conf

        # Parsing 3: Extract all nodes in the root directory
        new_con_obj_temp = con_obj.replace('\r', '').replace('\n', ''). \
            replace('<?xml version=\"1.0\" encoding=\"UTF-8\"?>', "")
        new_con_obj = re.sub(r'\sxmlns(:.*?)=".*?"|\sxmlns=".*?"', "", new_con_obj_temp)
        xml_to_dict = xmltodict.parse(new_con_obj)
        conf = xml_to_dict["data"]
        return conf

    def convert_to_set(self, d, xpath=''):
        '''
        Turn a dictionary into a collection
        :param d:
        :param xpath:
        :return:
        '''
        res = set()
        for key, val in d.items():
            if isinstance(val, dict):
                res = res | self.convert_to_set(val, xpath + "/" + key)
            elif isinstance(val, list):
                res.add((xpath + "/" + key, str(val)))
            else:
                res.add((xpath + "/" + key, val))
        return res

    def convert_to_dict(self, diff_s, dep, prefix):
        '''
        Turn the collection into a dictionary
        :param diff_s:
        :param dep:
        :param prefix:
        :return:
        '''
        if not diff_s:
            return {}
        res = dict()
        tmp_diff = {val for val in diff_s}
        for xpath, val in tmp_diff:
            if xpath.count("/") == dep:
                leaf_name = xpath[xpath.rfind("/") + 1:]
                prefix.update([xpath])
                res[leaf_name] = val
                diff_s.remove((xpath, val))
        tmp_diff = {val for val in diff_s}
        for xpath, val in tmp_diff:
            if xpath not in prefix:
                res.update({xpath.split("/")[dep]: self.convert_to_dict(diff_s, dep + 1, prefix)})
        return res

    # Compare the differences between the two dictionaries
    def compare_two_dict(self, existing, end_state):
        """
        # 1. Convert two dictionaries into a collection
        # 2. Take the intersection of the two sets
        # 3. Take the difference between end_state and intersection as update_dic
        # 4. Determine if update_dic is empty, if there is a value, changed to true
        """
        existing_set = self.convert_to_set(existing)
        end_state_set = self.convert_to_set(end_state)
        base = existing_set & end_state_set
        diff_s = end_state_set - base or existing_set - base
        update_dic = self.convert_to_dict(diff_s, 1, set())
        if update_dic:
            self.changed = True
        return dict(update_dic)

    def get_existing(self):
        """
        Get existing configuration parameters
        :return:
        """
        self.existing = self.netconf_get_config()

    def get_proposed(self):
        """
        Get proposed parameters
        :return:
        """
        for k, v in self.module.params.items():
            if k not in params_default_list and v:
                self.proposed[k] = v

    # Get the end_state parameters after execution
    def get_end_state(self):

        self.netconf_set_config()
        self.end_state = self.netconf_get_config()

    def get_update_cmd(self):
        """Get update_cmd parameters"""
        self.updates_cmd.append(
            self.compare_two_dict(self.existing, self.end_state))

    # Data returned to the user
    def show_result(self):
        """Show result"""
        # self.results['huawei'] = self.module.jsonify(self.translate_ietf)
        # self.results['ietf-routing'] = self.module.jsonify(self.ietf_routing)
        self.results['changed'] = self.changed
        self.results['end_state'] = self.end_state
        self.results['proposed'] = self.proposed

        self.results['existing'] = self.existing
        if self.changed:
          self.results['updates'] = self.updates_cmd
        else:
         self.results['updates'] = list()

        self.module.exit_json(**self.results)
        # self.module.exit_json(msg='ietf\n'+ self.ietf_routing+'\n\nhuawei\n'+self.translate_ietf)

    def run(self):
        """worker"""
        # module input info
        self.init_module()
        check_params(self.leaf_info, self.module.params, self.module)

        # return results
        self.get_proposed()
        self.get_existing()
        self.get_end_state()
        self.get_update_cmd()
        self.show_result()

class GetBase(object):
    """Create a GetBase class object"""

    def __init__(self, *args):
        self.argument_spec, self.leaf_info, self.namespaces, self.business_tag, self.xml_head, self.xml_tail,\
        self.key_list = args
        self.module = None

        # filter result state
        self.changed = False
        self.proposed = dict()
        self.results = dict()
        self.end_state = dict()

    def init_module(self):
        """ init module """
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True)
        return self.module

    def get_body_xml(self):
        """Construct the body part of the message."""
        new_params = {'root': self.module.params}
        body_xml_temp = parseString(self.params_to_xml(new_params)).toprettyxml()
        body_xml = body_xml_temp.replace('<?xml version="1.0" ?>', '')
        body_xml_list = re.compile(r"<root>(.*?)</root>", re.S).findall(body_xml)
        if not body_xml_list:
            return
        body_xml_str = body_xml_list[0]
        return body_xml_str

    def get_config_str(self):
        """Filter_get message stitching."""
        get_cfg_str = ''
        get_cfg_str += self.xml_head
        get_cfg_str += self.get_body_xml()
        get_cfg_str += self.xml_tail
        return get_cfg_str


    # get the data structure of instance xml from argument_spec
    def get_instance_xml_root(self, original_root):
        """
        :param original_root:  argument_spec
        :return result_dict:  find the xml's data structure from argument_spec.
        """
        result_dict = {}
        for key, value in original_root.items():
            if key not in params_default_list:
                result_dict[key] = value
        return result_dict

    def params_to_xml(self, params):
        """Convert params dictionary type to xml format."""
        root_value_filtered = self.get_instance_xml_root(params['root'])
        instance_xml_root = {"root": root_value_filtered}
        if instance_xml_root:
            for root_tag in instance_xml_root:
                root_tree = ET.Element(root_tag)
                self.to_xml(instance_xml_root[root_tag], root_tree)
            xmlstr = ET.tostring(root_tree, method='xml')
        return xmlstr

    # generate the body xml(Deep traversal dictionary)
    def to_xml(self, root_tree_dict, root_tree):
        """
        :param root_tree_dict:  the root of the data structure.
        :param root_tree:  the generate result.
        """
        for sub_node_tag, sub_node_value in root_tree_dict.items():
            if sub_node_tag != "get_all" and sub_node_tag != "get_value":
                # node exist in full.xml not in instance xml,do nothing
                if sub_node_value is None:
                    continue
                # node need to generate in xml
                elif isinstance(sub_node_value, list):
                    sub_element = ET.SubElement(root_tree, sub_node_tag)
                    for item in sub_node_value:
                        self.to_xml(item, sub_element)
                elif isinstance(sub_node_value, dict):
                    sub_element = ET.SubElement(root_tree, sub_node_tag)
                    # get value
                    value = None
                    for item in sub_node_value:
                        if item == "get_value":
                            value = sub_node_value[item]   # value: 1.int  2.str  3.boolean  4.None
                            break
                    if value is None:
                        value = ''
                    # <nodeName>True<nodeName> ---> <nodeName>true<nodeName>
                    if isinstance(value, bool):
                        value = str(value).lower()
                    # set value
                    if value or value == 0:
                        sub_element.text = str(value)

                    # get all status
                    all_status = False
                    for item in sub_node_value:
                        if item == "get_all":
                            all_status = sub_node_value[item]   # all: 1.True  2.False  3.None
                            break
                    if all_status is None:
                        all_status = False

                    # recursive
                    if all_status:
                        continue
                    else:
                        self.to_xml(sub_node_value, sub_element)
            else:
                continue

    def get_xml_str(self):
        """Get the xml which is get message."""
        get_cfg_str = self.get_config_str()
        cfg_str_to_doc = parseString(get_cfg_str).toxml()
        xml_list = [line.strip() for line in cfg_str_to_doc.split("\n") if line]
        update_xml = parseString(''.join(xml_list)).toprettyxml()
        get_str_temp = update_xml.replace('<?xml version="1.0" ?>', ''). \
            replace('type="subtree"', '')
        return get_str_temp

    def netconf_get_config(self):
        """The final Filter_get message is sent to the controlled machine."""
        xml_str = self.get_xml_str()
        get_str = xml_parser_join_xmlns(xml_str, self.namespaces, "filter")
        if HAS_MEDIATOR:
            translate_cfg_get = translate_query_filter_content(get_str)
        else:
            translate_cfg_get = get_str
        return self.get_info_process(translate_cfg_get)

    def get_config(self, module, xml_str, *args, **kwargs):
        """ get_config """
        conn = get_nc_connection(module)
        if xml_str is not None:
            try:
                response = conn.get_config(source='running', filter=xml_str)
            except ConnectionError as exc:
                module.fail_json(msg=to_text(exc))
            finally:
                pass
        else:
            return None
        return to_string(to_xml(response))

    # The get message is sent, and the current configuration parameters of the device are returned.
    def get_info_process(self, xml_str):
        """Get current dldp existed configuration"""
        conf = dict()
        # Send a get message
        # Parsing 1: delete the useless string, pay attention to the replacement according to the business
        if self.module.params["operation_type"] == "get":
            con_obj = get_nc_config(self.module, xml_str)
        else:  # ["operation_type"] == "get-config"
            con_obj = self.get_config(self.module, xml_str)
        #  Parsing 2: No data detection
        if "<data/>" in con_obj:
            return conf
        # Parsing 3: Extracting the echoed message
        new_con_obj_temp = con_obj.replace('\r', '').replace('\n', ''). \
            replace('<?xml version=\"1.0\" encoding=\"UTF-8\"?>', "")
        new_con_obj = re.sub(r'\sxmlns(:.*?)=".*?"|\sxmlns=".*?"', "", new_con_obj_temp)
        xml_to_dict = xmltodict.parse(new_con_obj)
        conf = {"result": xml_to_dict}
        return conf

    def get_proposed(self):
        """Get proposed  parameters."""
        for k, v in self.module.params.items():
            if k not in params_default_list and v:
                self.proposed[k] = v

    # get end_state parameters
    def get_end_state(self):
        '''
        get the end state
        :return:
        '''
        self.end_state = self.netconf_get_config()

    # Data returned to the user
    def show_result(self):
        """Show result"""
        self.results['changed'] = self.changed
        self.results['end_state'] = self.end_state
        self.results['proposed'] = self.proposed

        self.module.exit_json(**self.results)

    def run(self):
        """worker"""
        # module input info
        self.init_module()
        check_params(self.leaf_info, self.module.params, self.module)

        # return results
        self.get_proposed()
        self.get_end_state()
        self.show_result()

class InputBase(object):
    def __init__(self, *args):
        self.argument_spec, self.leaf_info, self.namespaces, self.business_tag, \
        self.xml_head, self.xml_tail, self.key_list = args
        self.module = None

        # config result state
        self.results = dict()

    def init_module(self):
        """ init module """
        self.module = AnsibleModule(
            argument_spec=self.argument_spec,
            supports_check_mode=True)
        return self.module

    def get_operation_type(self):
        """Get operation type"""
        self.init_module()
        return self.module.params

    def xml_tag(self, key, value):
        """Generate xml format for each line"""
        xml_str = ("<%s>{value}</%s>" % (key, key)) \
            .format(key=key, value=value if value is not None else '')
        return xml_str

    def to_xml(self, params):
        """Deep traversal of the dictionary and remove the default value."""
        xml_list = []
        for key, value in params.items():
            if isinstance(value, dict):
                xml_value = self.to_xml(value)
                xml_str = self.xml_tag(key, xml_value)
            elif isinstance(value, list):
                xml_value = ""
                for item in value:
                    xml_value = xml_value + self.to_xml(item)
                xml_str = self.xml_tag(key, xml_value)
            else:  # The type of value might be None/int/str/bool
                if value is None:
                    continue
                if type(value) == bool:
                    value = str(value).lower()
                xml_str = self.xml_tag(key, value)
            xml_list.append(xml_str)
        return ''.join(xml_list)

    def dict_order(self, business_params, leaf_info):
        temp_ordered_dict = OrderedDict()
        key_list = list(leaf_info.keys())
        for key in key_list:
            if isinstance(business_params, dict) and key in business_params.keys():
                temp_ordered_dict[key] = leaf_info[key]

        for key, value in business_params.items():
            if isinstance(value, dict):
                temp_ordered_dict[key] = self.dict_order(business_params[key], leaf_info[key])
            elif isinstance(value, list):
                temp_list = []
                for instance_dict in value:
                    temp_list.append(self.dict_order(instance_dict, leaf_info[key]))
                temp_ordered_dict[key] = temp_list
            else:
                temp_ordered_dict[key] = value
        return temp_ordered_dict

    def get_body_xml(self):
        """Config_set construct the body part of the message."""
        params_copy = copy.deepcopy(self.module.params)
        business_params = {}
        for business in self.business_tag:
            business_params[business] = params_copy[business]
        new_params = OrderedDict()
        new_params["root"] = self.dict_order(business_params, self.leaf_info)
        body_xml = parseString(self.to_xml(new_params)).toprettyxml()
        body_xml_list = re.compile(r"<root>(.*?)</root>", re.S).findall(body_xml)
        if not body_xml_list:
            return
        body_xml_str = body_xml_list[0]
        return body_xml_str

    # config_set Echo check function
    def check_response(self, xml_str):
        """Check if response message is already succeed."""
        conf = dict()
        if " <rpc-error>" not in xml_str:
            new_con_obj_temp = xml_str.replace('\r', '').replace('\n', ''). \
                replace('<?xml version=\"1.0\" encoding=\"UTF-8\"?>', "")
            new_con_obj = re.sub(r'\sxmlns(:.*?)=".*?"|\sxmlns=".*?"', "", new_con_obj_temp)
            xml_to_dict = xmltodict.parse(new_con_obj)
            conf = {"result": xml_to_dict}
        return conf

    def netconf_set_config(self, cfg_str):
        """The final config_set message is sent to the controlled machine."""
        cfg_str = "<rpc>" + cfg_str + "</rpc>"
        xml_str_with_xmlns = xml_parser_join_xmlns(cfg_str, self.namespaces, "rpc")
        send_xml_str = xml_str_with_xmlns.replace('<rpc>', "").replace('</rpc>', "")
        # Send a Get message
        # Parsing 1: delete the useless string, pay attention to the replacement according to the business
        con_obj = execute_nc_action_yang(self.module, send_xml_str)
        conf = self.check_response(con_obj)
        return conf

    # Data returned to the user
    def show_result(self):
        """Show result"""
        cfg_str = self.get_body_xml()
        xml_str = parseString(cfg_str).toprettyxml()
        self.results['send_xml'] = xmltodict.parse(xml_str)
        self.results['output'] = self.netconf_set_config(cfg_str)
        self.module.exit_json(**self.results)

    def run(self):
        """worker"""
        # module input info
        self.init_module()
        check_params(self.leaf_info, self.module.params, self.module)
        # return results
        self.show_result()

