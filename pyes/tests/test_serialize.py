#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'

import unittest
from pyes.tests import ESTestCase
from pyes import TermQuery, RangeQuery
from pyes.utils import ESRange
from datetime import datetime

"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""

class SerializationTestCase(ESTestCase):
    def setUp(self):
        super(SerializationTestCase, self).setUp()
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
                 u'inserted': {'store': 'yes',
                            'type': u'date'},
                 u'uuid': {'boost': 1.0,
                           'index': 'not_analyzed',
                           'store': 'yes',
                           'type': u'string'}}
        self.conn.create_index(self.index_name)
        self.conn.put_mapping(self.document_type, {'properties':mapping}, self.index_name)
        self.conn.index({"name":"Joe Tester", "parsedtext":"Joe Testere nice guy", "uuid":"11111", "position":1, 'inserted':datetime(2010, 10, 22, 12, 12, 12)}, self.index_name, self.document_type, 1)
        self.conn.index({"name":"Bill Baloney", "parsedtext":"Joe Testere nice guy", "uuid":"22222", "position":2, 'inserted':datetime(2010, 10, 22, 12, 12, 10)}, self.index_name, self.document_type, 2)
        self.conn.index({"name":"Jesus H Christ", "parsedtext":"Bible guy", "uuid":"33333", "position":3, 'inserted':datetime(1, 1, 1, 0, 0, 0)}, self.index_name, self.document_type, 3)
        self.conn.refresh(self.index_name)

    def test_TermQuery(self):
        q = TermQuery("name", "joe")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        hit = resultset[0]
        self.assertEquals(hit.inserted, datetime(2010, 10, 22, 12, 12, 12))

    def test_DateBefore1900(self):
        q = RangeQuery(ESRange("inserted", datetime(1, 1, 1), datetime(2, 1, 1)))
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        hit = resultset[0]
        self.assertEquals(hit.inserted, datetime(1, 1, 1, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
