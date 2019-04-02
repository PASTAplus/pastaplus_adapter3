#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_sys_meta

:Synopsis:

:Author:
    servilla
  
:Created:
    8/2/17
"""

from datetime import datetime
import logging
import xml.etree.ElementTree as ET

import unittest
import os
import sys

import adapter_utilities
import properties
from sys_meta import SysMeta


logger = logging.getLogger('test_sys_meta')
sys.path.insert(0, os.path.abspath('../src'))



class TestSysMeta(unittest.TestCase):
    resource_id = properties.PASTA_BASE_URL + 'metadata/eml/knb-lter-nin/1/1'
    owner_str = 'uid=LNO,o=LTER,dc=ecoinformatics,dc=org'
    access_policy = None

    def setUp(self):
        TestSysMeta.access_policy = access_policy()

    def tearDown(self):
        pass

    def test_d1_access_policy(self):
        sys_meta = SysMeta()
        sys_meta.access_policy = TestSysMeta.access_policy
        d1_access_policy = sys_meta.d1_access_policy(sys_meta.access_policy)
        xml = d1_access_policy.toxml()
        print(xml)
        self.assertIsNotNone(d1_access_policy)

    def test_d1_sys_meta(self):
        sys_meta = SysMeta()

        sys_meta.access_policy = TestSysMeta.access_policy
        sys_meta.checksum_value = 'e67809cb59c51ee456069e4cdb22bf2a7fb484b1'
        sys_meta.checksum_algorithm = 'SHA-1'
        sys_meta.file_name = 'LTER.NIN.DWS.csv'
        sys_meta.format_identifier = 'eml://ecoinformatics.org/eml-2.0.1'
        sys_meta.identifier = TestSysMeta.resource_id
        sys_meta.rights_holder = properties.DEFAULT_RIGHTS_HOLDER
        sys_meta.size = 48857

        d1_sys_meta = sys_meta.d1_sys_meta()
        xml = d1_sys_meta.toxml()
        print(xml)
        self.assertIsNotNone(d1_sys_meta)

def access_policy():
    # auth = (properties.GMN_USER, properties.GMN_PASSWD)
    # url = properties.PASTA_BASE_URL + 'metadata/acl/eml/knb-lter-nin/1/1'
    # r = adapter_utilities.requests_get_url_wrapper(url=url, auth=auth)
    # eml_acl = None
    # if r is not None:
    #     eml_acl = r.text.strip()

    with open('./data/acl.xml', 'r') as f:
        eml_acl = f.read()

    principal_owner = TestSysMeta.owner_str
    access_policy = []
    if eml_acl is not None:
        tree = ET.ElementTree(ET.fromstring(eml_acl))
        for allow_rule in tree.iter('allow'):
            principal = allow_rule.find('./principal')
            permission = allow_rule.find('./permission')
            access_policy.append(
                {'principal': principal.text,
                 'permission': permission.text})

    if principal_owner is not None:
        access_policy.append({'principal': principal_owner,
                    'permission': 'changePermission'})

    return access_policy



if __name__ == '__main__':
    unittest.main()