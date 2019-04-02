#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: adapter_utilities

:Synopsis:
 
:Author:
    servilla

:Created:
    3/8/17
"""

import logging
import pickle
import os.path
from datetime import datetime
from datetime import timedelta

import d1_client.cnclient_2_0
import requests

import properties


logger = logging.getLogger('adapter_utilities')
logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z',
                    # filename='$NAME' + '.log',
                    level=logging.INFO)

def _is_stale_file(filename=None, seconds=None):
    is_stale = False
    try:
        mtime = os.path.getmtime(filename=filename)
        delta = datetime.fromtimestamp(timestamp=mtime) + \
                timedelta(seconds=seconds)
        if delta < datetime.now():
            is_stale = True
    except OSError as e:
        logger.error(e)
        is_stale = True
    return is_stale


def get_d1_formats(url=properties.D1_BASE_URL):
    """Return dict of D1 formats as pyxb format object.

    Cache formats in "formats.pkl" pickle if D1 listformats()
    fails or if formats is stale based on file modify time.

    :param url: D1 base url
    :return: dict of D1 formats as pyxb format object
    """
    formats_file = properties.FORMATS
    formats = {}
    if _is_stale_file(filename=formats_file, seconds=3600):
        try:
            cn_client = \
                d1_client.cnclient_2_0.CoordinatingNodeClient_2_0(base_url=url)
            format_list = cn_client.listFormats()
            for _format in format_list.objectFormat:
                formats[_format.formatId] = _format
            fp = open(formats_file, 'wb')
            pickle.dump(formats, file=fp)
        except Exception as e:
            logger.error(e)
    try:
        fp = open(formats_file, 'rb')
        formats = pickle.load(file=fp)
    except IOError as e:
        logger.error(e)
    return formats


def make_http(url=None):
    return url.replace('https:', 'http:', 1)


def make_https(url=None):
    return url.replace('http:', 'https:', 1)


def requests_get_url_wrapper(url=None, auth=None):
    r = None
    try:
        r = requests.get(url=url, auth=auth)
        if r.status_code != requests.codes.ok:
            logger.error('Bad status code ({code}) for {url}'.format(
                code=r.status_code, url=url))
            r = None
    except Exception as e:
        logger.error(e)
    return r
