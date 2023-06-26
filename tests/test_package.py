#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_package

:Synopsis:

:Author:
    servilla
  
:Created:
    3/2/17
"""
from datetime import datetime

import daiquiri
import pytest

from event import Event
from package import Package
import properties

logger = daiquiri.getLogger(__name__)

PACKAGE_ID = "knb-lter-nin.1.1"
SCOPE = "knb-lter-nin"
IDENTIFIER = 1
REVISION = 1
DATETIME = datetime.strptime("2017-02-23T13:09:29.166", "%Y-%m-%dT%H:%M:%S.%f")
METHOD = "createDataPackage"
OWNER = "uid=LNO,o=EDI,dc=edirepository,dc=org"
DOI = "doi:10.6073/pasta/3bcc89b2d1a410b7a2c678e3c55055e1"
N_DATA_RESOURCES = 4
URL = properties.PASTA_BASE_URL


@pytest.fixture()
def package():
    event = Event()
    event.package = "knb-lter-nin.1.1"
    event.datetime = "2017-02-23T13:09:29.166"
    event.method = "createDataPackage"
    event.owner = "uid=LNO,o=EDI,dc=edirepository,dc=org"
    event.doi = "doi:10.6073/pasta/3bcc89b2d1a410b7a2c678e3c55055e1"
    return Package(event=event)


def test_package(package):
    assert PACKAGE_ID == package.package
    assert SCOPE == package.scope
    assert IDENTIFIER == package.identifier
    assert REVISION == package.revision
    assert DATETIME == package.datetime
    assert METHOD == package.method
    assert OWNER == package.owner
    assert N_DATA_RESOURCES == len(package.resources)
    assert DOI == package.doi
    assert package.public
