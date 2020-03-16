#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: package

:Synopsis:
    Create a data package object based on a PASTA event recorded in the
    adapter_queueu.sqlite database.

:Author:
    servilla

:Created:
    3/2/17
"""

import logging
import xml.etree.ElementTree as ET
import d1_common.types
import d1_common.xml

from adapter_exceptions import AdapterIncompleteStateException
import adapter_utilities
import properties
from resource import ResourceData
from resource import ResourceMetadata
from resource import ResourceOre
from resource import ResourceReport

logger = logging.getLogger('package')


class Package(object):

    def __init__(self, event=None):
        self._datetime = event.datetime
        self._doi = event.doi.strip()
        self._method = event.method.strip()
        self._owner = event.owner.strip()
        self._package = event.package.strip()
        self._scope, self._identifier, self._revision = self._package.split('.')
        self._package_path = self._package.replace('.', '/')
        self._resources = _build_resource_list(self.eml_url, self.package_url,
            self._owner, self._doi, self._package)
        self._public = _assert_package_is_public(self._resources)

    @property
    def datetime(self):
        return self._datetime

    @property
    def doi(self):
        return self._doi

    @property
    def method(self):
        return self._method

    @property
    def identifier(self):
        return int(self._identifier)

    @property
    def owner(self):
        return self._owner

    @property
    def package_path(self):
        return self._package_path

    @property
    def package_url(self):
        return properties.PASTA_BASE_URL + 'eml/' + self._package_path

    @property
    def eml_url(self):
        return properties.PASTA_BASE_URL + 'metadata/eml/' + self._package_path

    @property
    def package(self):
        return self._package

    @property
    def public(self):
        return self._public

    @property
    def resources(self):
        return self._resources

    @property
    def revision(self):
        return int(self._revision)

    @property
    def scope(self):
        return self._scope


def _assert_package_is_public(resources):
    """
    Asserts that the complete PASTA data package is publicly accessible

    :param resources: List of resources
    :return: Boolean
    """
    resource = resources[properties.METADATA]
    if not _assert_resource_is_public(resource.url):
        return False

    resource = resources[properties.REPORT]
    if not _assert_resource_is_public(resource.url):
        return False

    for resource in resources[properties.DATA]:
        if not _assert_resource_is_public(resource.url):
            return False
    return True


def _assert_resource_is_public(resource_url):
    """
    Asserts that the give PASTA resource is publicly accessible

    :param resource_url: The resource URL
    :return: Boolean
    """
    public = False
    url = properties.PASTA_BASE_URL + 'authz?resourceId=' + resource_url
    r = adapter_utilities.requests_get_url_wrapper(url=url)
    if r is not None:
        public = True
    return public


def _get_replication_policy(eml_url=None):
    r = adapter_utilities.requests_get_url_wrapper(url=eml_url)
    if r is not None:
        NAMESPACE_DICT = {
            'eml': 'eml://ecoinformatics.org/eml-2.1.1',
            'd1v1': 'http://ns.dataone.org/service/types/v1'
        }
        tree = ET.ElementTree(ET.fromstring(r.text))
        root = tree.getroot()
        replicationPolicy_list = root.findall(
            "additionalMetadata/metadata/d1v1:replicationPolicy", NAMESPACE_DICT)
        if len(replicationPolicy_list):
            return ET.tostring(replicationPolicy_list[0]).decode('utf-8')
    else:
        return None


def _generate_replication_policy(d1_replication_policy):
    if d1_replication_policy is None:
      return None
    return d1_common.types.dataoneTypes.CreateFromDocument(
      d1_replication_policy
    )


def _build_resource_list(eml_url, package_map_url, principal_owner, doi,
                         package_id):
    """
    Return a dict of data package resources without the reflexive package
    resource.

    :param package_map_url: PASTA package resource map url
    :param principal_owner: PASTA package principal owner
    :return: Dict of resource URLs
    """
    resources = {properties.METADATA: '',
                 properties.REPORT: '',
                 properties.ORE: '',
                 properties.DATA: []}

    package_acl = None
    replication_policy = _get_replication_policy(eml_url)
    if replication_policy is not None:
        replication_policy = _generate_replication_policy(replication_policy)

    url = package_map_url
    r = adapter_utilities.requests_get_url_wrapper(url=url)
    resource_urls = r.text.split()
    for resource_url in resource_urls:
        if properties.METADATA_PATTERN in resource_url:
            rm = ResourceMetadata(resource_url, principal_owner, package_id)
            rm.replication_policy = replication_policy
            resources[properties.METADATA] = rm
            package_acl = rm.acl
        elif properties.REPORT_PATTERN in resource_url:
            rr = ResourceReport(resource_url, principal_owner, package_id)
            rr.replication_policy = replication_policy
            resources[properties.REPORT] = rr
        elif properties.DATA_PATTERN in resource_url:
            rd = ResourceData(resource_url, principal_owner)
            rd.replication_policy = replication_policy
            resources[properties.DATA].append(rd)

    ro = ResourceOre(doi, principal_owner, resources, package_id)
    ro.acl = package_acl # Assign ORE same ACL as metadata/package ACL
    ro.replication_policy = replication_policy
    resources[properties.ORE] = ro

    return resources


def main():
    return 0


if __name__ == "__main__":
    main()
