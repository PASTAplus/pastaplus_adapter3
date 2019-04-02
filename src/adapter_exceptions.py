#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: adapter_exceptions

:Synopsis:
 
:Author:
    servilla

:Created:
    6/29/17
"""

import logging

logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z',
                    # filename='$NAME' + '.log',
                    level=logging.INFO)

logger = logging.getLogger('adapter_exceptions')


class AdapterUrlException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class AdapterUnknownResourceTypeException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class AdapterIncompleteStateException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)


class AdapterPackageNotPublicException(Exception):
    def __init__(self, value):
        self.value = value

    def __str__(self):
        return repr(self.value)
