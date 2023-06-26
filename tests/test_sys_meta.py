#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_sys_meta

:Synopsis:

:Author:
    servilla
  
:Created:
    8/2/17
"""
import daiquiri
import pytest
import xml.etree.ElementTree as ET

import properties
from sys_meta import SysMeta


logger = daiquiri.getLogger(__name__)


@pytest.fixture()
def test_system_metadata():
    attrs = {
        "resource_id": properties.PASTA_BASE_URL + "metadata/eml/knb-lter-nin/1/1",
        "access_policy": access_policy("uid=LNO,o=LTER,dc=ecoinformatics,dc=org")
    }
    return attrs


def test_d1_access_policy(test_system_metadata):
    sys_meta = SysMeta()
    sys_meta.access_policy = test_system_metadata["access_policy"]
    d1_access_policy = sys_meta.d1_access_policy(sys_meta.access_policy)
    xml = d1_access_policy.toxml()

    assert xml is not None


def test_d1_sys_meta(test_system_metadata):
    sys_meta = SysMeta()

    sys_meta.access_policy = test_system_metadata["access_policy"]
    sys_meta.checksum_value = 'e67809cb59c51ee456069e4cdb22bf2a7fb484b1'
    sys_meta.checksum_algorithm = 'SHA-1'
    sys_meta.file_name = 'LTER.NIN.DWS.csv'
    sys_meta.format_identifier = 'eml://ecoinformatics.org/eml-2.0.1'
    sys_meta.identifier = test_system_metadata["resource_id"]
    sys_meta.rights_holder = properties.DEFAULT_RIGHTS_HOLDER
    sys_meta.size = 48857

    d1_sys_meta = sys_meta.d1_sys_meta()
    xml = d1_sys_meta.toxml()

    assert xml is not None


def access_policy(principal_owner=None):
    # auth = (properties.GMN_USER, properties.GMN_PASSWD)
    # url = properties.PASTA_BASE_URL + 'metadata/acl/eml/knb-lter-nin/1/1'
    # r = adapter_utilities.requests_get_url_wrapper(url=url, auth=auth)
    # eml_acl = None
    # if r is not None:
    #     eml_acl = r.text.strip()

    with open('./data/acl.xml', 'r') as f:
        eml_acl = f.read()

    ap = []
    if eml_acl is not None:
        tree = ET.ElementTree(ET.fromstring(eml_acl))
        for allow_rule in tree.iter('allow'):
            principal = allow_rule.find('./principal')
            permission = allow_rule.find('./permission')
            ap.append(
                {'principal': principal.text,
                 'permission': permission.text})

    if principal_owner is not None:
        ap.append({'principal': principal_owner,
                   'permission': 'changePermission'})

    return ap
