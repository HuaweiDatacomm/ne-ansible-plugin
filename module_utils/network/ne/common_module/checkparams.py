#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re
import logging


def check_params(leaf_info, params, module):
    """Check all input params"""
    # Other parameters to be added to the synchronization to add
    # check
    return


def check_int(v_range, params, module):
    '''
    Check int type
    :param range:
    :param params:
    :param module:
    :return:
    '''
    if params and isinstance(params, dict):
        params = params["value"]
    if not params:
        return
    for long in v_range:
        if int(params) < int(long[0]) or int(params) > int(long[1]):
            logging.error('Error: %s not in the range from %s to %s.' % (params, long[0], long[1]))
            module.fail_json(msg='Error: %s not in the range from %s to %s.' % (params, long[0], long[1]))


def check_string(length, pattern, params, module):
    '''
    Check string type
    :param length:
    :param pattern:
    :param params:
    :param module:
    :return:
    '''
    if params and isinstance(params, dict):
        params = params["value"]
    if not params:
        return
    for long_str in length:
        if len(params) > long_str[1] or len(params.replace(' ', '')) < long_str[0]:
            logging.error('Error:%s is not in the range from %d to %d.' % (params, long_str[0], long_str[1]))
            module.fail_json(
                msg='Error:%s is not in the range from %d to %d.' % (params, long_str[0], long_str[1]))
    if pattern:
        for sub_re in pattern:
            if not re.match(sub_re, params):
                logging.error('Error:The input %s format is incorrect' % params)
                module.fail_json(msg='Error:The input %s format is incorrect' % params)
