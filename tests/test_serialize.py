# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from pyes.tests import ESTestCase
from pyes.query import TermQuery, RangeQuery
from pyes.utils import ESRange
from datetime import datetime

class SerializationTestCase(ESTestCase):
    def setUp(self):
        super(SerializationTestCase, self).setUp()
        mapping = {u'parsedtext': {'boost': 1.0,
                                   'index': 'analyzed',
                                   'store': 'true',
                                   'type': u'string',
                                   "term_vector": "with_positions_offsets"},
                   u'name': {'boost': 1.0,
                             'index': 'analyzed',
                             'store': 'true',
                             'type': u'string',
                             "term_vector": "with_positions_offsets"},
                   u'title': {'boost': 1.0,
                              'index': 'analyzed',
                              'store': 'true',
                              'type': u'string',
                              "term_vector": "with_positions_offsets"},
                   u'pos': {'store': 'true',
                            'type': u'integer'},
                   u'inserted': {'store': 'true',
                                 'type': u'date'},
                   u'uuid': {'boost': 1.0,
                             'index': 'not_analyzed',
                             'store': 'true',
                             'type': u'string'}}
        self.conn.indices.create_index(self.index_name)
        self.conn.indices.put_mapping(self.document_type, {'properties': self.get_default_mapping()}, self.index_name)
        self.conn.index({"name": "Joe Tester", "parsedtext": "Joe Testere nice guy", "uuid": "11111", "position": 1,
                         'inserted': datetime(2010, 10, 22, 12, 12, 12)}, self.index_name, self.document_type, 1)
        self.conn.index({"name": "Bill Baloney", "parsedtext": "Joe Testere nice guy", "uuid": "22222", "position": 2,
                         'inserted': datetime(2010, 10, 22, 12, 12, 10)}, self.index_name, self.document_type, 2)
        self.conn.index({"name": "Jesus H Christ", "parsedtext": "Bible guy", "uuid": "33333", "position": 3,
                         'inserted': datetime(1, 1, 1, 0, 0, 0)}, self.index_name, self.document_type, 3)
        self.conn.indices.refresh(self.index_name)

    def test_TermQuery(self):
        q = TermQuery("name", "joe")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)
        hit = resultset[0]
        self.assertEqual(hit.inserted, datetime(2010, 10, 22, 12, 12, 12))

    def test_DateBefore1900(self):
        q = RangeQuery(ESRange("inserted", datetime(1, 1, 1), datetime(2, 1, 1)))
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 0)
        # hit = resultset[0]
        # self.assertEqual(hit.inserted, datetime(1, 1, 1, 0, 0, 0))


if __name__ == "__main__":
    unittest.main()
