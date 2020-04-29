#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: event

:Synopsis:
    Provides a simple getter/setter container for adapter_queue database
    events.
 
:Author:
    servilla

:Created:
    8/8/17
"""
from datetime import datetime
import logging

import daiquiri


logger = daiquiri.getLogger(__name__)


class Event(object):
    """
    Event record to/from adapter_queue database
    """
    def __init__(self):
        self._package = None
        self._datetime = None
        self._method = None
        self._owner = None
        self._doi = None

    @property
    def datetime(self):
        """
        Returns an event database datetime object
        :return: Event datetime object
        """
        return self._datetime

    @datetime.setter
    def datetime(self, dt):
        """
        Sets an event database datetime object
        :param dt: Datetime string in '%Y-%m-%dT%H:%M:%S.%f' format
        """
        self._datetime = datetime.strptime(dt, '%Y-%m-%dT%H:%M:%S.%f')

    @property
    def doi(self):
        return self._doi

    @doi.setter
    def doi(self, d):
        self._doi = d

    @property
    def method(self):
        return self._method

    @method.setter
    def method(self, m):
        self._method = m

    @property
    def owner(self):
        return self._owner

    @owner.setter
    def owner(self, o):
        self._owner = o

    @property
    def package(self):
        return self._package

    @package.setter
    def package(self, p):
        self._package = p


def main():
    return 0


if __name__ == "__main__":
    main()