#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import re

DOCUMENTATION = """
description: get the ansible path.
"""


def get_ansible_path():
    '''
    get the ansible path
    '''
    res = os.popen('ansible --version').read()
    try:
        ansible_path = re.search(r'ansible python module location = (.*)', res).group(1)
    except Exception:
        raise Exception('No ansible_path!')
    return ansible_path


if __name__ == '__main__':
    a = get_ansible_path()
    print(a)
