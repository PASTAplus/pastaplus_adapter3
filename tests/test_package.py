#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_package

:Synopsis:

:Author:
    servilla
  
:Created:
    3/2/17
"""

import logging

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

import unittest
from datetime import datetime

from event import Event
from package import Package
import properties

logger = logging.getLogger('test_package')


class TestPackage(unittest.TestCase):
    package_str = 'knb-lter-nin.1.1'
    scope = 'knb-lter-nin'
    identifier = 1
    revision = 1
    datetime_str = '2017-02-23T13:09:29.166'
    datetime = datetime.strptime(datetime_str, '%Y-%m-%dT%H:%M:%S.%f')
    method = 'createDataPackage'
    owner = 'uid=LNO,o=LTER,dc=ecoinformatics,dc=org'
    doi = 'doi:10.6073/pasta/3bcc89b2d1a410b7a2c678e3c55055e1'
    number_of_resources = 3

    url = properties.PASTA_BASE_URL
    package = None

    @classmethod
    def setUpClass(cls):
        event = Event()
        event.package = 'knb-lter-nin.1.1'
        event.datetime = '2017-02-23T13:09:29.166'
        event.method = 'createDataPackage'
        event.owner = 'uid=LNO,o=LTER,dc=ecoinformatics,dc=org'
        event.doi = 'doi:10.6073/pasta/3bcc89b2d1a410b7a2c678e3c55055e1'
        TestPackage.package = Package(event=event)

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_package(self):
        package = TestPackage.package.package
        self.assertEqual(TestPackage.package_str, package)

    def test_scope(self):
        scope = TestPackage.package.scope
        self.assertEqual(TestPackage.scope, scope)

    def test_identifier(self):
        identifier = TestPackage.package.identifier
        self.assertEqual(TestPackage.identifier, identifier)

    def test_revision(self):
        revision = TestPackage.package.revision
        self.assertEqual(TestPackage.revision, revision)

    def test_datetime(self):
        datetime = TestPackage.package.datetime
        self.assertEqual(TestPackage.datetime, datetime)
        datetime_str = datetime.strftime('%Y-%m-%dT%H:%M:%S.%f').rstrip('0')
        self.assertEqual(TestPackage.datetime_str, datetime_str)

    def test_method(self):
        method = TestPackage.package.method
        self.assertEqual(TestPackage.method, method)

    def test_resources(self):
        cnt = 2 # Begin with 2 metadata and report resources
        resources = TestPackage.package.resources
        cnt += len(resources[properties.DATA])
        self.assertEqual(TestPackage.number_of_resources, cnt)

    def test_public(self):
        self.assertTrue(TestPackage.package.public)

    def test_get_doi(self):
        self.assertEqual(TestPackage.doi, TestPackage.package.doi)


if __name__ == '__main__':
    unittest.main()
