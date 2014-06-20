# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import logging
import unittest
from pprint import pprint
from pyes.es import ES
from pyes.helpers import SettingsBuilder

"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""

def get_conn(*args, **kwargs):
    return ES(("http", "127.0.0.1", 9200), *args, **kwargs)


class ESTestCase(unittest.TestCase):
    def setUp(self):
        self.log = open("/tmp/%s.sh"%self._testMethodName, "wb")
        self.conn = get_conn(timeout=300.0, log_curl=True, dump_curl=self.log)#incremented timeout for debugging
        self.index_name = "test-index"
        self.document_type = "test-type"
        self.conn.indices.delete_index_if_exists(self.index_name)

    def tearDown(self):
        self.conn.indices.delete_index_if_exists(self.index_name)
        if self.log:
            self.log.close()

    def assertResultContains(self, result, expected):
        for (key, value) in expected.items():
            found = False
            try:
                found = value == result[key]
            except KeyError:
                if result.has_key('meta'):
                    found = value == result['meta'][key]
            self.assertEqual(True, found)

    def checkRaises(self, excClass, callableObj, *args, **kwargs):
        """Assert that calling callableObj with *args and **kwargs raises an
        exception of type excClass, and return the exception object so that
        further tests on it can be performed.
        """
        try:
            callableObj(*args, **kwargs)
        except excClass as e:
            return e
        else:
            raise self.failureException("Expected exception %s not raised" % excClass)

    def get_datafile(self, filename):
        """
        Returns a the content of a test file
        """
        return open(os.path.join(os.path.dirname(__file__), "data", filename), "rb").read()

    def get_datafile_path(self, filename):
        """
        Returns a the content of a test file
        """
        return os.path.join(os.path.dirname(__file__), "data", filename)

    def dump(self, result):
        """
        dump to stdout the result
        """
        pprint(result)

    def init_default_index(self):
        settings = SettingsBuilder({'index.number_of_replicas': 0,
                                     "index.number_of_shards": 1})
        from pyes.mappings import DocumentObjectField
        from pyes.mappings import IntegerField
        from pyes.mappings import NestedObject
        from pyes.mappings import StringField, DateField

        docmapping = DocumentObjectField(name=self.document_type)
        docmapping.add_property(
            StringField(name="parsedtext", store=True, term_vector="with_positions_offsets", index="analyzed"))
        docmapping.add_property(
            StringField(name="name", store=True, term_vector="with_positions_offsets", index="analyzed"))
        docmapping.add_property(
            StringField(name="title", store=True, term_vector="with_positions_offsets", index="analyzed"))
        docmapping.add_property(IntegerField(name="position", store=True))
        docmapping.add_property(DateField(name="date", store=True))
        docmapping.add_property(StringField(name="uuid", store=True, index="not_analyzed"))
        nested_object = NestedObject(name="nested")
        nested_object.add_property(StringField(name="name", store=True))
        nested_object.add_property(StringField(name="value", store=True))
        nested_object.add_property(IntegerField(name="num", store=True))
        docmapping.add_property(nested_object)
        settings.add_mapping(docmapping)

        self.conn.ensure_index(self.index_name, settings)


def setUp():
    """Package level setup.

    For tests which don't modify the index, we don't want to have the overhead
    of setting up a test index, so we just set up test-pindex once, and use it
    for all tests.

    """
    mapping = {
        u'parsedtext': {
            'boost': 1.0,
            'index': 'analyzed',
            'store': 'yes',
            'type': u'string',
            "term_vector": "with_positions_offsets"},
        u'name': {
            'boost': 1.0,
            'index': 'analyzed',
            'store': 'yes',
            'type': u'string',
            "term_vector": "with_positions_offsets"},
        u'title': {
            'boost': 1.0,
            'index': 'analyzed',
            'store': 'yes',
            'type': u'string',
            "term_vector": "with_positions_offsets"},
        u'pos': {
            'store': 'yes',
            'type': u'integer'},
        u'doubles': {
            'store': 'yes',
            'type': u'double'},
        u'uuid': {
            'boost': 1.0,
            'index': 'not_analyzed',
            'store': 'yes',
            'type': u'string'}}

    conn = get_conn(log_curl=True)
    conn.indices.delete_index_if_exists("test-pindex")
    conn.indices.create_index("test-pindex")
    conn.indices.put_mapping("test-type", {'properties': mapping}, ["test-pindex"])
    conn.index({"name": "Joe Tester", "parsedtext": "Joe Testere nice guy", "uuid": "11111", "position": 1,
                "doubles": [1.0, 2.0, 3.0]}, "test-pindex", "test-type", 1)
    conn.index({"name": "Bill Baloney", "parsedtext": "Joe Testere nice guy", "uuid": "22222", "position": 2,
                "doubles": [0.1, 0.2, 0.3]}, "test-pindex", "test-type", 2)
    conn.indices.refresh(["test-pindex"])


def tearDown():
    """Remove the package level index.

    """
    conn = get_conn()
    conn.indices.delete_index_if_exists("test-pindex")
