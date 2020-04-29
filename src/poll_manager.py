#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: parser

:Synopsis:
 
:Author:
    servilla

:Created:
    3/5/17
"""

import logging
from datetime import datetime
from datetime import timedelta
import os
import xml.etree.ElementTree as ET

import daiquiri
import pendulum

from adapter_exceptions import AdapterRequestFailureException
import adapter_utilities
from event import Event
from lock import Lock
import properties
from queue_manager import QueueManager


cwd = os.path.dirname(os.path.realpath(__file__))
logfile = cwd + "/poll_manager.log"
daiquiri.setup(level=logging.INFO,
               outputs=(daiquiri.output.File(logfile), "stdout",))
logger = daiquiri.getLogger(__name__)


def bootstrap(url=None):
    now = datetime.now()
    fromDate = datetime.strptime(properties.FROM_DATE,
                                 '%Y-%m-%dT%H:%M:%S.%f')

    while fromDate < now:
        toDate = fromDate + timedelta(minutes=30)
        logger.warning('from: {f} -- to: {t}'.format(f=str(fromDate), t=str(toDate)))
        parse(url=url, fromDate=fromDate, toDate=toDate, scope=properties.SCOPE)
        fromDate = toDate


def parse(url=None, fromDate=None, toDate=None, scope=None):
    """
    Parse the PASTA list of changes XML based on the query parameters provided
     
    :param url: changes URL as a String
    :param fromDate: fromDate as a datetime
    :param toDate: toDate as a datetime
    :param scope: scope filter value (only one) as a String for changes
                     query
    :return: 0 if successful, 1 otherwise
    """

    msg = f'parse params: url-{url}, fromDate-{fromDate}, toDate-{toDate},' + \
          f' scope-{scope}'
    logger.info(msg) 

    # convert to string representations
    fromDate = datetime.strftime(fromDate, '%Y-%m-%dT%H:%M:%S.%f')
    if toDate is not None:
        toDate = datetime.strftime(toDate, '%Y-%m-%dT%H:%M:%S.%f')

    # add date(s) to url
    if fromDate is not None:
        url = url + 'fromDate=' + fromDate
    if toDate is not None:
        url = url + '&toDate=' + toDate
    if scope is not None:
        url = url + '&scope=' + scope

    logger.info('requests_get_url_wrapper: ' + url)
    r = adapter_utilities.requests_get_url_wrapper(url=url, rethrow=True)

    if r is not None:
        qm = QueueManager()
        tree = ET.ElementTree(ET.fromstring(r.text.strip()))
        for dataPackage in tree.iter('dataPackage'):
            package = dataPackage.find('./packageId')
            date = dataPackage.find('./date')
            method = dataPackage.find('./serviceMethod')
            owner = dataPackage.find('./principal')
            doi = dataPackage.find('./doi')

            event = Event()
            event.package = package.text
            event.datetime = date.text
            event.method = method.text
            event.owner = owner.text
            event.doi = doi.text

            # Skip fromDate record(s) that already exist in queue
            if fromDate.rstrip('0') == date.text:
                msg = 'Skipping: {} - {} - {}'.format(package.text, date.text,
                                                      method.text)
                logger.warning(msg)
            else:
                # Provide additional filter for multiple scope values
                package_scope = event.package.split('.')[0]
                if package_scope in properties.PASTA_WHITELIST:
                    msg = 'Enqueue: {} - {} - {}'.format(package.text,
                                                         date.text, method.text)
                    logger.warning(msg)
                    qm.enqueue(event=event)
                else:
                    logger.info('Package {} out of scope'.format(package.text))


def main():

    lock = Lock('/tmp/poll_manager.lock')
    if lock.locked:
        logger.error('Lock file {} exists, exiting...'.format(lock.lock_file))
        return 1
    else:
        lock.acquire()
        logger.warning('Lock file {} acquired'.format(lock.lock_file))

    url = properties.PASTA_BASE_URL + 'changes/eml?'
    qm = QueueManager()

    # queue fromDate (fallback): effective but not efficient
    fromDate = qm.get_last_datetime()
    logger.info(f'"fromDate" from QueueManager: {fromDate}')

    if fromDate is None: # Empty adapter_queue database
        bootstrap(url=url)
    else:
        fromDate = pendulum.instance(dt=fromDate, tz='US/Mountain')
        last_query_date = adapter_utilities.get_last_query_date()
        if last_query_date is not None:
            # pickled fromDate: effective and efficient
            fromDate = last_query_date.in_tz('US/Mountain')
            logger.info(f'"fromDate" from adapter_utilities: {fromDate}')

        try:
            query_date = pendulum.now(tz='UTC')
            parse(url=url, fromDate=fromDate, scope=properties.SCOPE)
            adapter_utilities.save_last_query_date(query_date)
        except AdapterRequestFailureException as e:
            logger.error(e)

    lock.release()
    logger.warning('Lock file {} released'.format(lock.lock_file))
    return 0


if __name__ == "__main__":
    main()

