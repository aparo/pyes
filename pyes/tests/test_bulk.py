#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""
import unittest
from pyes.tests import ESTestCase
from pyes import TermQuery

class BulkTestCase(ESTestCase):
    def setUp(self):
        super(BulkTestCase, self).setUp()
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
        
    def test_force(self):
        self.conn.index({"name":"Joe Tester", "parsedtext":"Joe Testere nice guy", "uuid":"11111", "position":1}, self.index_name, self.document_type, 1, bulk=True)
        self.conn.index({"name":"Bill Baloney", "parsedtext":"Bill Testere nice guy", "uuid":"22222", "position":2}, self.index_name, self.document_type, 2, bulk=True)
        self.conn.index({"name":"Bill Clinton", "parsedtext":"""Bill is not 
                nice guy""", "uuid":"33333", "position":3}, self.index_name, self.document_type, 3, bulk=True)
        bulk_result = self.conn.force_bulk()
        self.assertEquals(len(bulk_result['items']), 3)
        self.conn.refresh(self.index_name)
        q = TermQuery("name", "bill")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 2)
        
    def test_automatic_flush(self):
        self.conn.force_bulk()
        self.conn.bulk_size = 3
        
        self.assertIsNone(
            self.conn.index({"name":"Joe Tester", "parsedtext":"Joe Testere nice guy", "uuid":"11111", "position":1},
                self.index_name, self.document_type, 4, bulk=True))
        self.assertIsNone(self.conn.flush_bulk(False))
        self.assertEqual(len(self.conn.bulk_data), 1)
        
        self.assertIsNone(
            self.conn.index({"name":"Bill Baloney", "parsedtext":"Bill Testere nice guy", "uuid":"22222", "position":2},
                self.index_name, self.document_type, 5, bulk=True))
        self.assertIsNone(self.conn.flush_bulk(False))
        self.assertEqual(len(self.conn.bulk_data), 2)
        
        bulk_result = self.conn.index(
            {"name":"Bill Clinton", "parsedtext":"""Bill is not nice guy""", "uuid":"33333", "position":3},
                self.index_name, self.document_type, 6, bulk=True)
        self.assertEquals(len(bulk_result['items']), 3)
        self.assertEqual(self.conn.bulk_data, [])
        
        self.conn.bulk_size = 3
        
        self.assertIsNone(self.conn.delete(self.index_name, self.document_type, 4, True))
        self.assertIsNone(self.conn.flush_bulk(False))
        self.assertEqual(len(self.conn.bulk_data), 1)

        self.assertIsNone(self.conn.delete(self.index_name, self.document_type, 5, True))
        self.assertIsNone(self.conn.flush_bulk(False))
        self.assertEqual(len(self.conn.bulk_data), 2)
        
        bulk_result = self.conn.delete(self.index_name, self.document_type, 6, True)
        self.assertIsNone(self.conn.flush_bulk(False))
        self.assertEquals(len(bulk_result['items']), 3)
        self.assertEqual(self.conn.bulk_data, [])
        
        self.conn.refresh(self.index_name)

if __name__ == "__main__":
    unittest.main()
