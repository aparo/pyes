#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""
import unittest
from pyes.tests import ESTestCase
from pyes import *
from time import sleep

class MultifieldTestCase(ESTestCase):
    def setUp(self):
        super(MultifieldTestCase, self).setUp()
        mapping = { u'parsedtext': {'boost': 1.0,
                         'index': 'analyzed',
                         'store': 'yes',
                         'type': u'string',
                         "term_vector" : "with_positions_offsets"},
                 u'title': {'boost': 1.0,
                            'index': 'analyzed',
                            'store': 'yes',
                            'type': u'string',
                            "term_vector" : "with_positions_offsets"},
                u'name': {"type" : "multi_field",
                                  "fields":{
                                     u'name':{
                                        u'boost': 1.0,
                                         u'index': u'analyzed',
                                         u'omit_norms': False,
                                         u'omit_term_freq_and_positions': False,
                                         u'store': u'yes',
                                         "term_vector" : "with_positions_offsets",
                                         u'type': u'string'},
                                     u'untouched':{u'boost': 1.0,
                                         u'index': u'not_analyzed',
                                         u'omit_norms': False,
                                         u'omit_term_freq_and_positions': False,
                                         u'store': u'yes',
                                         "term_vector" : "no",
                                         u'type': u'string'}
                                        
                                        }

                 },
                 u'pos': {'store': 'yes',
                            'type': u'integer'},
                 u'uuid': {'boost': 1.0,
                           'index': 'not_analyzed',
                           'store': 'yes',
                           'type': u'string'}}
        self.conn.create_index("test-index")
        res = self.conn.put_mapping("test-type", {'properties':mapping}, ["test-index"])
        self.dump(res)
        self.conn.index({"name":"Joe Tester", "parsedtext":"Joe Testere nice guy", "uuid":"11111", "position":1}, "test-index", "test-type", 1)
        self.conn.index({"name":"Bill Baloney", "parsedtext":"Joe Testere nice guy", "uuid":"22222", "position":2}, "test-index", "test-type", 2)
        self.conn.refresh(["test-index"])

        #Sleep to allow ElasticSearch to set up 
        #mapping and indices before running tests
        #sleep(0.5)

    def test_TermQuery(self):
        q = TermQuery("name", "joe")
        result = self.conn.search(query = q, indexes=["test-index"])
        self.assertEquals(result['hits']['total'], 1)

        q = TermQuery("name", "joe", 3)
        result = self.conn.search(query = q, indexes=["test-index"])
        self.assertEquals(result['hits']['total'], 1)
        
        q = TermQuery("name", "joe", "3")
        result = self.conn.search(query = q, indexes=["test-index"])
        self.assertEquals(result['hits']['total'], 1)


if __name__ == "__main__":
    unittest.main()