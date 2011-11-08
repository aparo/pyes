#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""
import unittest
from pyes.tests import ESTestCase
from pyes import Search, StringQuery, HighLighter

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
        self.conn.create_index(self.index_name)
        self.conn.put_mapping(self.document_type, {'properties':mapping}, self.index_name)
        self.conn.index({"name":"Joe Tester", "parsedtext":"Joe Testere nice guy", "uuid":"11111", "position":1}, self.index_name, self.document_type, 1)
        self.conn.index({"name":"Bill Baloney", "parsedtext":"Joe Testere nice guy", "uuid":"22222", "position":2}, self.index_name, self.document_type, 2)
        self.conn.index({"parsedtext":"Joe Testere nice guy", "uuid":"22222", "position":2}, self.index_name, self.document_type, 2)
        self.conn.refresh(self.index_name)

    def test_QueryHighlight(self):
        q = Search(StringQuery("joe"))
        q.add_highlight("parsedtext")
        q.add_highlight("name")
        resultset = self.conn.search(q, indices=self.index_name)

        print resultset[0].meta.highlight

        self.assertEquals(resultset.total, 2)
        self.assertNotEqual(resultset[0].meta.highlight, None)

        self.assertEquals(resultset[0].meta.highlight[u"parsedtext"][0],
                          u'<em>Joe</em> Testere nice guy ')

    def test_QueryHighlightWithHighLighter(self):
        h = HighLighter(['<b>'], ['</b>'])
        q = Search(StringQuery("joe"), highlight=h)
        q.add_highlight("parsedtext")
        q.add_highlight("name")
        resultset = self.conn.search(q, indices=self.index_name)

        print resultset[0].meta.highlight

        self.assertEquals(resultset.total, 2)
        self.assertNotEqual(resultset[0].meta.highlight, None)

        self.assertEquals(resultset[0].meta.highlight[u"parsedtext"][0],
                          u'<b>Joe</b> Testere nice guy ')

if __name__ == "__main__":
    unittest.main()
