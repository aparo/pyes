#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Unit tests for pyes.  These require an es server running on the default port (127.0.0.1:9500).
"""
import unittest
from tests import ESTestCase
from query import *
from query_extra import *
from pprint import pprint


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
                 u'uuid': {'boost': 1.0,
                           'index': 'not_analyzed',
                           'store': 'yes',
                           'type': u'string'}}
        self.conn.create_index("test-index")
        self.conn.put_mapping("test-type", {'properties':mapping}, ["test-index"])
        self.conn.index({"name":"Joe Tester", "parsedtext":u"Città è in prosperità", "uuid":"11111", "position":1}, "test-index", "test-type", 1)
        self.conn.index({"name":"Bill Baloney", "parsedtext":"Joe Testere nice guy", "uuid":"22222", "position":2}, "test-index", "test-type", 2)
        self.conn.index({"name":"Bill Tester", "parsedtext":u"La metropoli è in prosperità", "uuid":"3333", "position":3}, "test-index", "test-type", 3)
        self.conn.index({"name":"Bill Bugs", "parsedtext":u"Strano insieme di abitazioni", "uuid":"4444", "position":4}, "test-index", "test-type", 4)
        self.conn.refresh(["test-index"])

    def test_NLPinAll(self):
        """
        Test search in all
        """
#        q = NLPQuery(u"città", "it")
#        result = self.conn.search(query = q, indexes="test-index")
#        self.assertEquals(result['hits']['total'], 1)

        q = NLPQuery(u"insieme di abitazioni", "it")
        q.add_highlight("name")
        q.add_highlight("parsedtext")
        q.add_highlight("title")
        result = self.conn.search(query = q, indexes="test-index")
        self.assertEquals(result['hits']['total'], 1)


#    def test_NLPQuery(self):
#        q = NLPQuery(["parsedtext", "name"], u"città", "it")
#        result = self.conn.search(query = q, indexes="test-index")
##        pprint(result)
#        self.assertEquals(result['hits']['total'], 1)
#
#
#        q = NLPQuery(["parsedtext", "name"], u"città", "it")
#        q.add_option("use_synonyms")
#        print q
#        result = self.conn.search(query = q, indexes=["test-index"])
##        pprint(result)
#        self.assertEquals(result['hits']['total'], 2)
#
##        q = NLPQuery(["parsedtext", "name"], u"città", "it")
##        q.add_option("hypernym")
##        result = self.conn.search(query = q, indexes=["test-index"])
###        pprint(result)
##        self.assertEquals(result['hits']['total'], 2)
##
##        q = NLPQuery(["parsedtext", "name"], u"città", "it")
##        q.add_option("hyponym")
##        result = self.conn.search(query = q, indexes=["test-index"])
###        pprint(result)
##        self.assertEquals(result['hits']['total'], 2)


if __name__ == "__main__":
    unittest.main()