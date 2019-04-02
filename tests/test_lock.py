#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_lock

:Synopsis:

:Author:
    servilla
  
:Created:
    3/31/17
"""

import logging

logger = logging.getLogger('test_lock')

import unittest
import os
import sys

sys.path.insert(0, os.path.abspath('../src'))

from lock import Lock


class TestLock(unittest.TestCase):

    def setUp(self):
        self.lock = Lock('bozo.lock')

    def tearDown(self):
        try:
            self.lock.release()
        except IOError as e:
            logger.error(e)

    def test_acquire_release(self):
        print(self.lock.acquire())
        try:
            self.lock.release()
        except IOError as e:
            logger.error(e)
            self.fail()
        self.lock.acquire()

    def test_locked(self):
        self.lock.acquire()
        self.assertTrue(self.lock.locked)


if __name__ == '__main__':
    unittest.main()