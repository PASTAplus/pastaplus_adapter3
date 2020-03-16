#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: resource

:Synopsis:

:Author:
    servilla

:Created:
    3/10/17
"""

import logging
import hashlib
import xml.etree.ElementTree as ET

import requests
import d1_common.resource_map
import d1_common.types.exceptions
import d1_common.types.generated.dataoneTypes_v1 as dataoneTypes_v_1
import d1_common.types.generated.dataoneTypes_v2_0 as dataoneTypes_v2_0

import adapter_exceptions
import adapter_utilities
import properties
from sys_meta import SysMeta

logger = logging.getLogger('resource')


class ResourceBase(object):

    def __init__(self, url, owner):
        logger.info(f'Building resource: {url}')
        self._acl = None
        self._checksum_value = None
        self._checksum_algorithm = None
        self._d1_sys_meta = None
        self._file_name = None
        self._format_identifier = None
        self._identifier = url
        self._object = None
        self._owner = owner
        self._package_id = None
        self._predecessor = None
        self._replication_policy = None
        self._rights_holder = properties.DEFAULT_RIGHTS_HOLDER
        self._size = None
        self._url = url
        self._vendor_specific_header = None

    def _get_checksum_value(self, path, replacement):
        """
        Set the checksum value and algorithm for the given resource

        :param path: PASTA resource path fragment
        :param replacement: Modified path fragment for checksum value
        :return: None
        """
        url = self._url.replace(path, replacement)
        r = adapter_utilities.requests_get_url_wrapper(url=url)
        if r is not None:
            return r.text.strip()

    def _get_acl(self, path, replacement):
        """
        Return the EML access control list of principals and permissions

        :param path: PASTA resource path fragment
        :param replacement: Modified path fragment for PASTA EML ACL
        :param owner: Data package principal owner
        :return: Access control list
        """
        auth = (properties.GMN_USER, properties.GMN_PASSWD)
        eml_acl = None
        url = self._url.replace(path, replacement)
        r = adapter_utilities.requests_get_url_wrapper(url=url, auth=auth)
        if r is not None:
            eml_acl = r.text.strip()
        acl = []
        if eml_acl is not None:
            tree = ET.ElementTree(ET.fromstring(eml_acl))
            for allow_rule in tree.iter('allow'):
                principal = allow_rule.find('./principal')
                permission = allow_rule.find('./permission')
                acl.append(
                    {'principal': principal.text,
                     'permission': permission.text})
        if self._owner is not None:
            acl.append({'principal': self._owner,
                        'permission': 'changePermission'})
        return acl


    @property
    def acl(self):
        return self._acl

    @acl.setter
    def acl(self, a):
        self._acl = a

    @property
    def replication_policy(self):
        return self._replication_policy

    @replication_policy.setter
    def replication_policy(self, rp):
        self._replication_policy = rp
 
    def get_d1_sys_meta(self):
        """
        Return a D1 system metadata object for the given resource as pyxb
        object.

        :return: D1 system metadata as a pyxb object
        """
        sm = SysMeta()
        sm.access_policy = self._acl
        sm.checksum_algorithm = self._checksum_algorithm
        sm.checksum_value = self._checksum_value
        sm.file_name = self._file_name
        sm.format_identifier = self._format_identifier
        sm.identifier = self._identifier
        sm.replication_policy = self._replication_policy
        sm.rights_holder = self._rights_holder
        sm.size = self._size

        return sm.d1_sys_meta()

    @property
    def identifier(self):
        return self._identifier

    @property
    def object(self):
        return self._object

    @property
    def owner(self):
        return self._owner

    @property
    def url(self):
        return self._url

    @property
    def vendor_specific_header(self):
        return self._vendor_specific_header


class ResourceMetadata(ResourceBase):

    def __init__(self, url, owner, package_id):
        super(ResourceMetadata,self).__init__(url, owner)
        self._acl = self._get_acl('/metadata/eml/', '/metadata/acl/eml/')
        self._checksum_value = \
            self._get_checksum_value('/metadata/eml/', '/metadata/checksum/eml/')
        self._checksum_algorithm = properties.CHECKSUM_ALGORITHM
        self._file_name = f"{package_id}.xml"
        self._format_identifier = self._get_format_id()
        self._size = self._get_size()
        self._vendor_specific_header = {'VENDOR-GMN-REMOTE-URL': url}

    def _get_format_id(self):
        d1_formats = adapter_utilities.get_d1_formats()
        format_id = None
        url = self._url.replace('/metadata/eml/', '/metadata/format/eml/')
        r = adapter_utilities.requests_get_url_wrapper(url=url)
        if r is not None:
            eml_version = r.text.strip()
            if eml_version in d1_formats:
                format_id = d1_formats[eml_version].formatId
        return format_id

    def _get_size(self):
        size = None
        r = adapter_utilities.requests_get_url_wrapper(url=self._url)
        if r is not None:
            size = int(r.headers['Content-Length'])
        return size

    @property
    def predecessor(self):
        return self._predecessor

    @predecessor.setter
    def predecessor(self, pred):
        identifier = properties.PASTA_BASE_URL + 'metadata/eml/' + \
                     pred.replace('.', '/')
        self._predecessor = identifier


class ResourceReport(ResourceBase):

    def __init__(self, url, owner, package_id):
        super(ResourceReport,self).__init__(url, owner)
        self._acl = self._get_acl('/report/eml/', '/report/acl/eml/')
        self._checksum_value = \
            self._get_checksum_value('/report/eml/', '/report/checksum/eml/')
        self._checksum_algorithm = properties.CHECKSUM_ALGORITHM
        self._file_name = f"{package_id}-report.xml"
        self._format_identifier = 'text/xml'
        self._size = self._get_size()
        self._vendor_specific_header = {'VENDOR-GMN-REMOTE-URL': url}

    def _get_size(self):
        size = None
        r = adapter_utilities.requests_get_url_wrapper(url=self._url)
        if r is not None:
            size = int(r.headers['Content-Length'])
        return size


class ResourceData(ResourceBase):

    def __init__(self, url, owner):
        super(ResourceData,self).__init__(url, owner)
        self._acl = self._get_acl('/data/eml/', '/data/acl/eml/')
        self._checksum_value = \
            self._get_checksum_value('/data/eml/', '/data/checksum/eml/')
        self._checksum_algorithm = properties.CHECKSUM_ALGORITHM
        self._file_name = self._get_file_name()
        self._format_identifier = self._get_format_id()
        self._size = self._get_size()
        self._vendor_specific_header = {'VENDOR-GMN-REMOTE-URL': url}

    def _get_file_name(self):
        file_name = None
        url = self._url.replace('/data/eml', '/data/rmd/eml')
        r = adapter_utilities.requests_get_url_wrapper(url=url)
        if r is not None:
            rmd = r.text.strip()
        if rmd is not None:
            tree = ET.ElementTree(ET.fromstring(rmd))
            _ = tree.find(".//fileName")
            file_name = _.text
        return file_name

    def _get_format_id(self):
        d1_formats = adapter_utilities.get_d1_formats()
        format_id = None
        try:
            r = requests.head(self._url, allow_redirects=True)
            if r.status_code == requests.codes.ok:
                content_type = r.headers['Content-Type']
                if content_type in d1_formats:
                    format_id = d1_formats[content_type].formatId
                else:
                    format_id = 'application/octet-stream'
        except Exception as e:
            logger.error(e)
        return format_id

    def _get_size(self):
        size = None
        url = self._url.replace('/data/eml/', '/data/size/eml/')
        r = adapter_utilities.requests_get_url_wrapper(url=url)
        if r is not None:
            size = int(r.text.strip())
        return size


class ResourceOre(ResourceBase):

    def __init__(self, doi, owner, resources, package_id):
        super(ResourceOre,self).__init__(doi, owner)
        ore_xml = _build_ore(pid=doi, resources=resources)
        self._checksum_algorithm = 'SHA-1'
        self._checksum_value = hashlib.sha1(ore_xml).hexdigest()
        self._file_name = f"{package_id}-ore.xml"
        self._format_identifier = 'http://www.openarchives.org/ore/terms'
        self._object = ore_xml
        self._resources = None
        self._size = len(ore_xml)

    @property
    def predecessor(self):
        return self._predecessor

    @predecessor.setter
    def predecessor(self, doi):
        self._predecessor = doi


def _build_ore(pid=None, resources=None):
    data = []
    data.append(resources[properties.METADATA].identifier)
    data.append(resources[properties.REPORT].identifier)
    for data_resource in resources[properties.DATA]:
        data.append(data_resource.identifier)

    ore = d1_common.resource_map.ResourceMap(base_url=properties.D1_BASE_URL)
    ore.initialize(pid=pid)
    ore.addMetadataDocument(pid=resources[properties.METADATA].identifier)
    ore.addDataDocuments(scidata_pid_list=data, scimeta_pid=resources[properties.METADATA].identifier)
    return ore.serialize()
