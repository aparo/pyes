#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Issue #6 testcase.
"""
import unittest
from pyes.tests import ESTestCase
from pyes import *
from time import sleep

class QuerySearchTestCase(ESTestCase):
    def setUp(self):
        super(QuerySearchTestCase, self).setUp()
        mapping = { u'parsedtext': {'boost': 1.0,
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
                 u'doubles': {'store': 'yes',
                            'type': u'double'},
                 u'uuid': {'boost': 1.0,
                           'index': 'not_analyzed',
                           'store': 'yes',
                           'type': u'string'}}
        self.conn.create_index("test-index")
        self.conn.put_mapping("test-type", {'properties':mapping}, ["test-index"])
        self.conn.index({"name":"Joe Tester", "parsedtext":"Joe Testere nice guy", "uuid":"11111", "position":1, "doubles":[1.0, 2.0, 3.0]}, "test-index", "test-type", 1)
        self.conn.index({"name":"Bill Baloney", "parsedtext":"Joe Testere nice guy", "uuid":"22222", "position":2, "doubles":[0.1, 0.2, 0.3]}, "test-index", "test-type", 2)
        self.conn.refresh(["test-index"])

        #Sleep to allow ElasticSearch to set up 
        #mapping and indices before running tests
        #sleep(0.5)
        
    def test_ReconvertDoubles(self):
        q = MatchAllQuery()
        result = self.conn.search(query = q, indexes=["test-index"])
        self.assertEquals(result['hits']['total'], 2)

if __name__ == "__main__":
    unittest.main()