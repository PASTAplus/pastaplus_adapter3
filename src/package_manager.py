#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import print_function

""":Mod: package_manager

:Synopsis:

:Author:
    servilla

:Created:
    3/8/17
"""

import logging
from io import BytesIO
import time


# Set level to WARN to avoid verbosity in requests at INFO
logging.basicConfig(format='%(asctime)s %(levelname)s (%(name)s): %(message)s',
                    datefmt='%Y-%m-%d %H:%M:%S%z', level=logging.WARN)

import xml.etree.ElementTree as ET

import d1_client.cnclient_2_0
import d1_client.mnclient_2_0

from adapter_exceptions import AdapterIncompleteStateException
from lock import Lock
from package import Package
import properties
from queue_manager import QueueManager


logger = logging.getLogger('package_manager')


def create_gmn_client():
    return d1_client.mnclient_2_0.MemberNodeClient_2_0(
        base_url=properties.GMN_BASE_URL,
        cert_pem_path=properties.GMN_CERT_PATH,
        cert_key_path=properties.GMN_KEY_PATH,
        verify_tls=properties.VERIFY_TLS
    )


def get_replication_policy(eml_xml=None):
    NAMESPACE_DICT = {
        'eml': 'eml://ecoinformatics.org/eml-2.1.1',
        'd1v1': 'http://ns.dataone.org/service/types/v1'
    }
    tree = ET.ElementTree(ET.fromstring(eml_xml))
    root = tree.getroot()
    replicationPolicy_list = root.findall(
        "additionalMetadata/metadata/d1v1:replicationPolicy", NAMESPACE_DICT)
    if len(replicationPolicy_list):
        return ET.tostring(replicationPolicy_list[0])


def gmn_create(resource=None):
    logger.warn('Create: {}'.format(resource.identifier))
    gmn_client = create_gmn_client()
    try:
        gmn_client.create(pid=resource.identifier,
                          obj=BytesIO(resource.object),
                          sysmeta_pyxb=resource.get_d1_sys_meta(),
                          vendorSpecific=resource.vendor_specific_header)
    except Exception as e:
        logger.debug('gmn_create exception - pid={} object={}'.format(resource.identifier, resource.object))
        logger.error(e)


def gmn_update(resource=None):
    logger.warn('Update: {}'.format(resource.identifier))
    gmn_client = create_gmn_client()
    try:
        gmn_client.update(pid=resource.predecessor,
                          obj=BytesIO(resource.object),
                          newPid = resource.identifier,
                          sysmeta_pyxb=resource.get_d1_sys_meta(),
                          vendorSpecific=resource.vendor_specific_header)
        pass
    except Exception as e:
        logger.error(e)


def gmn_archive(resource=None):
    logger.warn('Archive: {}'.format(resource.identifier))
    gmn_client = create_gmn_client()
    try:
        gmn_client.archive(pid=resource.identifier)
    except Exception as e:
        logger.error(e)


def gmn_exists(pid=None):
    gmn_client = create_gmn_client()
    try:
        r = gmn_client.getChecksum(pid)
    except Exception as e:
        logger.error(e)
        return False
    return True


def process_create_package(package=None):
    r = package.resources
    gmn_create(r[properties.METADATA])
    gmn_create(r[properties.REPORT])
    data_resources = r[properties.DATA]
    for rd in data_resources:
        gmn_create(rd)
    gmn_create(r[properties.ORE])


def process_update_package(package=None, queue_manager=None):

    predecessor = queue_manager.get_predecessor(package.package)
    while predecessor is not None:
        p = Package(predecessor)
        if p.public:
            break
        else:
            predecessor = queue_manager.get_predecessor(predecessor.package)

    r = package.resources

    rm = r[properties.METADATA]
    if predecessor is not None:
        rm.predecessor = predecessor.package
        gmn_update(rm)
    else:
        gmn_create(rm)

    gmn_create(r[properties.REPORT])

    data_resources = r[properties.DATA]
    for rd in data_resources:
        gmn_create(rd)

    ro = r[properties.ORE]
    if predecessor is not None:
        ro.predecessor = predecessor.doi
        gmn_update(ro)
    else:
        gmn_create(ro)


def process_archive_package(package=None):
    r = package.resources
    gmn_archive(r[properties.METADATA])
    gmn_archive(r[properties.REPORT])
    data_resources = r[properties.DATA]
    for rd in data_resources:
        gmn_archive(rd)
    gmn_archive(r[properties.ORE])


def main():

    lock = Lock('/tmp/package_manager.lock')
    if lock.locked:
        logger.error('Lock file {} exists, exiting...'.format(lock.lock_file))
        return 1
    else:
        lock.acquire()
        logger.warn('Lock file {} acquired'.format(lock.lock_file))

    qm = QueueManager()
    head = qm.get_head()
    while head is not None:
        logger.warn('Active package: {p}'.format(p=head.package))
        skip = False
        if properties.CHECK_PRE_EXISTENCE_IN_GMN and head.method in [properties.CREATE, properties.UPDATE]:
            skip = gmn_exists(properties.PASTA_BASE_URL + 'metadata/eml/' + head.package.replace('.', '/'))
        if skip:
            logger.warn('Package already exists: {}. Skipping {}.'.format(head.package, head.method))
        else:
            p = Package(head)
            if p.public:
                logger.warn('Processing: {p}'.format(p=p.package))
                resource = p.resources[properties.METADATA]
                if p.method == properties.CREATE:
                    process_create_package(package=p)
                elif p.method == properties.UPDATE:
                    process_update_package(package=p, queue_manager=qm)
                elif p.method == properties.DELETE:
                    process_archive_package(package=p)
                else:
                    msg = 'Unrecognized package event "{event}" for' \
                          'package: {package}'.format(event=p.method,
                                                      package=p.package)
                    raise(AdapterIncompleteStateException(msg))
            else:
                logger.warn('Package not public: {p}'.format(p=p.package))
        
        qm.dequeue(package=head.package, method=head.method)
        if properties.SLEEP_BETWEEN_PACKAGES:
            time.sleep(int(properties.SLEEP_BETWEEN_PACKAGES))
        head = qm.get_head()

    logger.warn('Queue empty')
    lock.release()
    logger.warn('Lock file {} released'.format(lock.lock_file))
    return 0


if __name__ == "__main__":
    main()
