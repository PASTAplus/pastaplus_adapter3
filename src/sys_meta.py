#!/usr/bin/env python
# -*- coding: utf-8 -*-

""":Mod: sys_meta

:Synopsis:
    Provides a class and tools to manage a DataONE v2 system metadata.
 
:Author:
    servilla

:Created:
    8/2/17
"""

import logging

import d1_common.types.generated.dataoneTypes_v1 as dataoneTypes_v_1
import d1_common.types.generated.dataoneTypes_v2_0 as dataoneTypes_v2_0

from adapter_exceptions import AdapterIncompleteStateException


logger = logging.getLogger('sys_meta')


class SysMeta(object):

    def __init__(self):
        self._access_policy = None
        self._checksum_algorithm = None
        self._checksum_value = None
        self._file_name = None
        self._format_identifier = None
        self._identifier = None
        self._replication_policy = None
        self._rights_holder = None
        self._size = None

    def _assert_complete_sys_meta(self):
        msg = list()
        if self._checksum_algorithm is None:
            msg.append('checksum algorithm')
        if self._checksum_value is None:
            msg.append('checksum value')
        if self._file_name is None:
            msg.append('filename value')
        if self._format_identifier is None:
            msg.append('format identifier')
        if self._identifier is None:
            msg.append('identifier')
        if self._rights_holder is None:
            msg.append('rights holder')
        if self._size is None:
            msg.append('size')
        if len(msg) > 0:
            msg = ', '.join([_ for _ in msg])
            msg = (
                f'One or more of the following system metadata attribute(s) '
                f'is missing: {msg}'
            )
            raise(AdapterIncompleteStateException(msg))

    @property
    def access_policy(self):
        return self._access_policy

    @access_policy.setter
    def access_policy(self, access_policy):
        """
        Sets the access policy as a list of dictionary tuples consisting of
        'principal' and 'permissions'.

        :param access_policy:
        :return:
        """
        self._access_policy = access_policy

    @property
    def checksum_algorithm(self):
        return self._checksum_algorithm

    @checksum_algorithm.setter
    def checksum_algorithm(self, checksum_algorithm):
        self._checksum_algorithm = checksum_algorithm

    @property
    def checksum_value(self):
        return self._checksum_value

    @checksum_value.setter
    def checksum_value(self, checksum_value):
        self._checksum_value = checksum_value

    def d1_access_policy(self, access_policy=None):
        """
        Return a DataONE system metadata access policy object based on the
        generated access policy found for the resource.

        :param access_policy: Local resource access policy as a list of
               principals and permissions.
        :return: DataONE access policy as pyxb object
        """
        accessPolicy = dataoneTypes_v_1.accessPolicy()

        if access_policy is not None:
            for policy in access_policy:
                accessRule = dataoneTypes_v_1.AccessRule()
                accessRule.subject.append(policy['principal'])
                accessRule.permission.append(policy['permission'])
                accessPolicy.append(accessRule)

        return accessPolicy

    def d1_sys_meta(self):
        """
        Return a D1 v2.0 system metadata pyxb object; all required elements
        must be present before the pyxb object may be created.

        :return: D1 v2.0 system metadata pyxb object
        """

        self._assert_complete_sys_meta()

        d1_sys_meta = dataoneTypes_v2_0.systemMetadata()

        d1_sys_meta.accessPolicy = self.d1_access_policy(self._access_policy)
        d1_sys_meta.checksum = dataoneTypes_v_1.Checksum(self._checksum_value)
        d1_sys_meta.checksum.algorithm = self._checksum_algorithm
        d1_sys_meta.fileName = self._file_name
        d1_sys_meta.formatId = self._format_identifier
        d1_sys_meta.identifier = self._identifier
        d1_sys_meta.replicationPolicy = self._replication_policy
        d1_sys_meta.rightsHolder = self._rights_holder
        d1_sys_meta.size = self._size

        return d1_sys_meta

    @property
    def file_name(self):
        return self._file_name

    @file_name.setter
    def file_name(self, file_name):
        self._file_name = file_name

    @property
    def format_identifier(self):
        return self._format_identifier

    @format_identifier.setter
    def format_identifier(self, format_identifier):
        self._format_identifier = format_identifier

    @property
    def identifier(self):
        return self._identifier

    @identifier.setter
    def identifier(self, identifier):
        self._identifier = identifier

    @property
    def replication_policy(self):
        return self._replication_policy

    @replication_policy.setter
    def replication_policy(self, replication_policy):
        self._replication_policy = replication_policy

    @property
    def rights_holder(self):
        return self._rights_holder

    @rights_holder.setter
    def rights_holder(self, rights_holder):
        self._rights_holder = rights_holder

    @property
    def size(self):
        return self._size

    @size.setter
    def size(self, size):
        self._size = size


def main():
    return 0


if __name__ == "__main__":
    main()