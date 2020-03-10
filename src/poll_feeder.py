#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import sys
import time

from adapter_exceptions import AdapterRequestFailureException
import click
from event import Event
from lock import Lock
import properties
from queue_manager import QueueManager
from sqlalchemy import create_engine


@click.command()
@click.argument("package_id")
def poll_feeder(
    package_id: str
):
    """
    Given a package ID in the form scope.identifier.revision (e.g., edi.1.1),
    queries the PASTA database to get the package's details and creates an event
    in the pastaplus GMN adapter's poll_manager queue so the package will be
    processed in due course by the package_manager.
    """

    # Check the Python version
    if sys.version_info < (3, 6):
        print("Requires Python 3.6 or later")
        exit(0)

    main(package_id)


logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=properties.LOG_LEVEL)
logger = logging.getLogger('poll_feeder')


def connect():
    db = properties.DB_DRIVER + '://' + \
        properties.DB_USER + ':' + \
        properties.DB_PW + '@' + \
        properties.DB_HOST + '/' + \
        properties.DB_DB

    connection = create_engine(db)
    return connection


def get_package_info(connection, scope, identifier, target_revision):
    """
    Query PASTA for package info and return an Event object for insertion into the poll_manager queue.
    """
    sql = (f'''select scope, identifier, revision, doi, principal_owner, date_created from datapackagemanager.resource_registry 
               where resource_type='dataPackage' and scope='{scope}' and identifier='{identifier}' order by scope, identifier, revision''')
    logger.info(sql)
    result_set = connection.execute(sql).fetchall()
    revisions = []
    event = None
    for scope, identifier, revision, doi, principal_owner, date_created in result_set:
        revisions.append(revision)
        if revision == int(target_revision):
            event = Event()
            event.package = '.'.join([scope, str(identifier), str(revision)])
            event.datetime = date_created.strftime('%Y-%m-%dT%H:%M:%S.%f')
            event.owner = principal_owner
            event.doi = doi
    if event:
        if sorted(revisions).index(int(target_revision)) == 0:
            event.method = 'createDataPackage'
        else:
            event.method = 'updateDataPackage'
    return event


def main(package_id=None):
    logger.info(f'package_id={package_id}')

    lock = Lock('/tmp/poll_manager.lock')
    if lock.locked:
        logger.error('Lock file {} exists, exiting...'.format(lock.lock_file))
        return 1
    else:
        lock.acquire()
        logger.warning('Lock file {} acquired'.format(lock.lock_file))

    try:
        scope, identifier, revision = package_id.split('.')

        connection = connect()
        event = get_package_info(connection, scope, identifier, revision)

        if event:
            qm = QueueManager()

            msg = f'Enqueue: {event.package} - {event.datetime} - {event.owner} - {event.doi} - {event.method}'
            logger.warning(msg)
            qm.enqueue(event=event)

    except AdapterRequestFailureException as e:
        logger.error(e)

    lock.release()
    logger.warning('Lock file {} released'.format(lock.lock_file))
    return 0


if __name__ == "__main__":
    poll_feeder()

