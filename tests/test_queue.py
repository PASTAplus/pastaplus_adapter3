#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

""":Mod: test_adapter_db

:Synopsis:

:Author:
    servilla
  
:Created:
    3/3/17
"""

from datetime import datetime
import logging
import unittest

from event import Event
from package import Package
from queue_manager import QueueManager

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.INFO)

logger = logging.getLogger('test_queue')


class TestAdapterQueue(unittest.TestCase):

    def setUp(self):
        self.qm = QueueManager(queue='test_adapter_queue.sqlite')
        self.build_packages()

    def tearDown(self):
        self.qm.delete_queue()

    def test_enqueue(self):
        e = Event()
        e.package = 'edi.3.2'
        e.datetime = '2017-01-03T14:30:56.673000'
        e.method = 'createDataPackage'
        e.owner = 'uid=SBC,o=LTER,dc=ecoinformatics,dc=org'
        e.doi = 'doi:10.5072/FK2/381addd8bfda02f8ba85329df8f903dc'
        self.qm.enqueue(event=e)
        self.assertEquals(self.qm.get_count(),1)

    def test_get_head(self):
        self.enqueue_all()
        e = self.qm.get_head()
        self.assertEquals(e.package, self.events[0].package)

    def test_dequeue(self):
        self.enqueue_all()
        e = self.qm.get_head()
        self.qm.dequeue(package=e.package, method=e.method)
        e = self.qm.get_head()
        self.assertEquals(e.package, self.events[1].package)

    def test_get_last_datetime(self):
        self.enqueue_all()
        datetime = self.qm.get_last_datetime()
        self.assertEqual(self.events[9].datetime, datetime)

    def test_get_predecessor(self):
        self.enqueue_all()
        e = self.events[5]
        p = self.qm.get_predecessor(package=e.package)
        self.assertEqual(self.events[4].package, p.package)

    def build_packages(self):
        e0 = Event()
        e0.package = 'edi.3.2'
        e0.datetime = '2017-01-03T14:30:56.673000'
        e0.method = 'createDataPackage'
        e0.owner = 'uid=SBC,o=LTER,dc=ecoinformatics,dc=org'
        e0.doi = 'doi:10.5072/FK2/381addd8bfda02f8ba85329df8f903dc'

        e1 = Event()
        e1.package = 'edi.3002.1'
        e1.datetime = '2017-06-02T17:46:57.154000'
        e1.method = 'createDataPackage'
        e1.owner = 'uid=LNO,o=LTER,dc=ecoinformatics,dc=org'
        e1.doi = 'doi:10.5072/FK2/55fcb5e7de4634cc332d4f874d0caf73'

        e2 = Event()
        e2.package = 'edi.98.1'
        e2.datetime = '2017-06-14T17:20:47.138000'
        e2.method = 'createDataPackage'
        e2.owner = 'uid=EDI,o=LTER,dc=ecoinformatics,dc=org'
        e2.doi = 'doi:10.5072/FK2/0ffb0cde729f2e1bf97e9a7f7acc9d57'

        e3 = Event()
        e3.package = 'edi.98.2'
        e3.datetime = '2017-06-14T17:45:30.938000'
        e3.method = 'updateDataPackage'
        e3.owner = 'uid=EDI,o=LTER,dc=ecoinformatics,dc=org'
        e3.doi = 'doi:10.5072/FK2/c21403aa2cf1fc0535b7a3a21f3b3852'

        e4 = Event()
        e4.package = 'edi.98.3'
        e4.datetime = '2017-06-14T18:31:31.549000'
        e4.method = 'updateDataPackage'
        e4.owner = 'uid=EDI,o=LTER,dc=ecoinformatics,dc=org'
        e4.doi = 'doi:10.5072/FK2/586c753cc9adbc6102d0a3b458cbfb1c'

        e5 = Event()
        e5.package = 'edi.98.4'
        e5.datetime = '2017-06-14T19:01:20.551000'
        e5.method = 'updateDataPackage'
        e5.owner = 'uid=EDI,o=LTER,dc=ecoinformatics,dc=org'
        e5.doi = 'doi:10.5072/FK2/f6b49227664aaac91675a785e29bc12f'

        e6 = Event()
        e6.package = 'edi.100.1'
        e6.datetime = '2017-06-14T19:04:00.470000'
        e6.method = 'createDataPackage'
        e6.owner = 'uid=EDI,o=LTER,dc=ecoinformatics,dc=org'
        e6.doi = 'doi:10.5072/FK2/d9b8652cd4f1a63935af87f19387351c'

        e7 = Event()
        e7.package = 'edi.100.2'
        e7.datetime = '2017-06-14T19:09:20.009000'
        e7.method = 'updateDataPackage'
        e7.owner = 'uid=EDI,o=LTER,dc=ecoinformatics,dc=org'
        e7.doi = 'doi:10.5072/FK2/2aa459937b15c7133a48828a54b9a249'

        e8 = Event()
        e8.package = 'edi.100.1'
        e8.datetime = '2017-06-15T13:13:29.717000'
        e8.method = 'deleteDataPackage'
        e8.owner = 'uid=EDI,o=LTER,dc=ecoinformatics,dc=org'
        e8.doi = 'doi:10.5072/FK2/d9b8652cd4f1a63935af87f19387351c'

        e9 = Event()
        e9.package = 'edi.100.2'
        e9.datetime = '2017-06-15T13:13:29.717000'
        e9.method = 'deleteDataPackage'
        e9.owner = 'uid=EDI,o=LTER,dc=ecoinformatics,dc=org'
        e9.doi = 'doi:10.5072/FK2/2aa459937b15c7133a48828a54b9a249'

        self.events = (e0, e1, e2, e3, e4, e5, e6, e7, e8, e9)

    def enqueue_all(self):
        for event in self.events:
            self.qm.enqueue(event=event)


if __name__ == '__main__':
    unittest.main()
