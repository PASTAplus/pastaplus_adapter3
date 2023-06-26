#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: test_lock

:Synopsis:

:Author:
    servilla
  
:Created:
    3/31/17
"""
import pathlib

import daiquiri
import pytest

from lock import Lock


logger = daiquiri.getLogger(__name__)
LOCK_FILE = "bozo.lock"


@pytest.fixture()
def lock():
    return Lock(LOCK_FILE)


def test_acquire_release(lock):
    lock.acquire()
    assert pathlib.Path(LOCK_FILE).exists()

    lock.release()
    assert not pathlib.Path(LOCK_FILE).exists()
