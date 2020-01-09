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
import os
import os.path
from datetime import datetime
from datetime import timedelta

import d1_client.cnclient_2_0
import requests

import properties
from adapter_exceptions import AdapterRequestFailureException

logger = logging.getLogger('adapter_utilities')
logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z',
                    # filename='$NAME' + '.log',
                    level=logging.WARN)


def _is_stale_file(filename=None, seconds=None):
    is_stale = False
    try:
        mtime = os.path.getmtime(filename=filename)
        delta = datetime.fromtimestamp(timestamp=mtime) + timedelta(seconds=seconds)
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


def requests_get_url_wrapper(url=None, auth=None, rethrow=False):
    r = None
    try:
        r = requests.get(url=url, auth=auth)
        if r.status_code != requests.codes.ok:
            logger.error('Bad status code ({code}) for {url}'.format(
                code=r.status_code, url=url))
            r = None
    except Exception as e:
        logger.error(e)
        if rethrow:
            raise AdapterRequestFailureException
    return r


def save_last_query_date(query_date=None):
    # number of minutes to subtract from query_date
    # we provide a generous amount of "slop" to allow for the possibility that PASTA's clock isn't
    #   synced perfectly with ours
    # it doesn't hurt to save a last_query_date that's in the past, since the date will keep moving
    #   forward in any case
    SAFETY_MARGIN = 60

    if query_date is None:
        query_date = datetime.now()
    query_date -= timedelta(minutes=SAFETY_MARGIN)
    last_query_file = properties.LAST_QUERY
    try:
        with open(last_query_file, 'wb') as fp:
            logger.info('save_last_query_date ' + str(query_date))
            pickle.dump(query_date, file=fp)
    except Exception as e:
        logger.error(e)


def clear_last_query_date():
    last_query_file = properties.LAST_QUERY
    if os.path.exists(last_query_file):
        logger.info('clear_last_query_date')
        os.remove(last_query_file)


def get_last_query_date():
    last_query_file = properties.LAST_QUERY
    last_query_date = None
    try:
        with open(last_query_file, 'rb') as fp:
            last_query_date = pickle.load(file=fp)
    except FileNotFoundError as e:
        pass
    except Exception as e:
        logger.error(e)
    logger.info('get_last_query_date returns ' + str(last_query_date))
    return last_query_date

