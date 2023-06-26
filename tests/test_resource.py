#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

""":Mod: test_resource

:Synopsis:

:Author:
    servilla
  
:Created:
    3/10/17
"""
from datetime import datetime

import daiquiri
import pytest

import properties
from resource import ResourceMetadata
from resource import ResourceOre


logger = daiquiri.getLogger(__name__)


@pytest.fixture()
def one_resource():
    resource = {
        "package_str": "knb-lter-nin.1.1",
        "scope": "knb-lter-nin",
        "identifier": 1,
        "revision": 1,
        "datetime": datetime.strptime("2017-02-23T13:09:29.166", "%Y-%m-%dT%H:%M:%S.%f"),
        "method": "createDataPackage",
        "owner": "uid=LNO,o=LTER,dc=ecoinformatics,dc=org",
        "doi": "doi:10.6073/pasta/3bcc89b2d1a410b7a2c678e3c55055e1",
        "url": properties.PASTA_BASE_URL,
        "scimeta_size": 48856, # For https://pasta-d.lternet.edu/package/metadata/eml/knb-lter-nin/1/1
        "metadata_resource": properties.PASTA_BASE_URL + "metadata/eml/knb-lter-nin/1/1",
        "report_resource": properties.PASTA_BASE_URL + "report/eml/knb-lter-nin/1/1",
        "data_resource": properties.PASTA_BASE_URL + "data/eml/knb-lter-nin/1/1/67e99349d1666e6f4955e9dda42c3cc2",
    }

    return resource


def test_resource_method(one_resource):
    rm = ResourceMetadata(one_resource["metadata_resource"],
                          one_resource["owner"],
                          one_resource["package_str"])
    assert rm is not None


def test_resource_ore(one_resource):
    metadata_resource = Resource(one_resource["metadata_resource"])
    report_resource = Resource(one_resource["report_resource"])
    data_resource = Resource(one_resource["data_resource"])

    resources = {properties.METADATA: metadata_resource,
                 properties.REPORT: report_resource,
                 properties.ORE: '',
                 properties.DATA: [data_resource]}

    ore_resource = ResourceOre(one_resource["doi"],
                     one_resource["owner"],
                     resources,
                     one_resource["package_str"])

    system_metadata = ore_resource.get_d1_sys_meta()

    assert ore_resource is not None
    assert system_metadata is not None


def test_build_system_metadata(one_resource):
    metadata_resource = ResourceMetadata(one_resource["metadata_resource"],
                                         one_resource["owner"],
                                         one_resource["package_str"])
    system_metadata = metadata_resource.get_d1_sys_meta()

    assert system_metadata is not None


class Resource:
    """
    Mock Resource class containing only the "identifier" attribute
    """

    def __init__(self, identifier):
        self._identifier = identifier

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, id):
        self._identifier = id
