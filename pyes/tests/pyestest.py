#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""

import unittest
from pyes import ES
from pprint import pprint
from pyes.helpers import SettingsBuilder

def get_conn(*args, **kwargs):
    return ES(("http", "127.0.0.1", 9200), *args, **kwargs)

class ESTestCase(unittest.TestCase):

    def setUp(self):
        self.conn = get_conn(timeout=300.0)#incremented timeout for debugging
        self.index_name = "test-index"
        self.document_type = "test-type"
        self.conn.delete_index_if_exists(self.index_name)

    def tearDown(self):
        self.conn.delete_index_if_exists(self.index_name)

    def assertResultContains(self, result, expected):
        for (key, value) in expected.items():
            found = False
            try:
                found = value == result[key]
            except KeyError:
                if result.has_key('meta'):
                    found = value == result['meta'][key]
            self.assertEquals(True, found)

            #self.assertEquals(value, result[key])

    def checkRaises(self, excClass, callableObj, *args, **kwargs):
        """Assert that calling callableObj with *args and **kwargs raises an
        exception of type excClass, and return the exception object so that
        further tests on it can be performed.
        """
        try:
            callableObj(*args, **kwargs)
        except excClass, e:
            return e
        else:
            raise self.failureException, \
                "Expected exception %s not raised" % excClass

    def dump(self, result):
        """
        dump to stdout the result
        """
        pprint(result)

    def init_default_index(self):
        settings = SettingsBuilder()
        settings.add_mapping({self.document_type:{'properties':
                { u'parsedtext': {'boost': 1.0,
                                 'index': 'analyzed',
                                 'store': 'yes',
                                 'type': u'string',
                                 "term_vector" : "with_positions_offsets"},
                         u'name': {'boost': 1.0,
                                    'index': 'analyzed',
                                    'store': 'yes',
                                    'type': u'string',
                                    "term_vector" : "with_positions_offsets"},
                         u'title': {'boost': 1.0,
                                    'index': 'analyzed',
                                    'store': 'yes',
                                    'type': u'string',
                                    "term_vector" : "with_positions_offsets"},
                         u'pos': {'store': 'yes',
                                    'type': u'integer'},
                         u'uuid': {'boost': 1.0,
                                   'index': 'not_analyzed',
                                   'store': 'yes',
                                   'type': u'string'}}
                          }}, name=self.document_type)

        self.conn.create_index(self.index_name, settings)

main = unittest.main
