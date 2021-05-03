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
import logging
import unittest
from datetime import datetime

import properties
from resource import ResourceMetadata
from resource import ResourceOre

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

logger = logging.getLogger('test_resource')


class TestResource(unittest.TestCase):
    package_str = 'knb-lter-nin.1.1'
    scope = 'knb-lter-nin'
    identifier = 1
    revision = 1
    datetime_str = '2017-02-23T13:09:29.166'
    datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
    method = 'createDataPackage'
    owner = 'uid=LNO,o=LTER,dc=ecoinformatics,dc=org'
    doi = 'doi:10.6073/pasta/3bcc89b2d1a410b7a2c678e3c55055e1'
    url = properties.PASTA_BASE_URL
    scimeta_size = 48856 # For https://pasta-d.lternet.edu/package/metadata/eml/knb-lter-nin/1/1

    metadata_resource = properties.PASTA_BASE_URL + \
                        'metadata/eml/knb-lter-nin/1/1'
    report_resource = properties.PASTA_BASE_URL + 'report/eml/knb-lter-nin/1/1'
    data_resource = properties.PASTA_BASE_URL + \
                    'data/eml/knb-lter-nin/1/1/67e99349d1666e6f4955e9dda42c3cc2'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def testResourceMetadata(self):
        rm = ResourceMetadata(TestResource.metadata_resource,
                              TestResource.owner,
                              TestResource.package_str)
        self.assertIsNotNone(rm)

    def testResourceOre(self):
        rm = Resource(TestResource.metadata_resource)
        rr = Resource(TestResource.report_resource)
        rd = Resource(TestResource.data_resource)

        resources = {properties.METADATA: rm,
                     properties.REPORT: rr,
                     properties.ORE: '',
                     properties.DATA: [rd]}

        ro = ResourceOre(TestResource.doi,
                         TestResource.owner,
                         resources,
                         TestResource.package_str)
        sm = ro.get_d1_sys_meta()
        self.assertIsNotNone(ro)

    def test_build_system_metadata(self):
        rm = ResourceMetadata(TestResource.metadata_resource,
                              TestResource.owner,
                              TestResource.package_str)
        sm = rm.get_d1_sys_meta()
        self.assertIsNotNone(sm)


class Resource(object):
    """
    Mock Resource class containing only the "identifier" attribute
    """

    def __init__(self, identifier):
        self._indentifier = identifier

    @property
    def identifier(self):
        return self._indentifier

    @identifier.setter
    def identifier(self, id):
        self._identifier = id


if __name__ == '__main__':
    unittest.main()
