# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from pyes.tests import ESTestCase
from pyes.query import TermQuery


class MultifieldTestCase(ESTestCase):
    def setUp(self):
        super(MultifieldTestCase, self).setUp()
        mapping = {u'parsedtext': {'boost': 1.0,
                                   'index': 'analyzed',
                                   'store': 'yes',
                                   'type': u'string',
                                   "term_vector": "with_positions_offsets"},
                   u'title': {'boost': 1.0,
                              'index': 'analyzed',
                              'store': 'yes',
                              'type': u'string',
                              "term_vector": "with_positions_offsets"},
                   u'name': {"type": "multi_field",
                             "fields": {
                                 u'name': {
                                     u'index': u'analyzed',
                                     u'store': u'yes',
                                     u'type': u'string'},
                                 u'untouched': {
                                     u'index': u'not_analyzed',
                                     u'store': u'yes',
                                     u'type': u'string'}

                             }

                   },

                   u'pos': {'store': 'yes',
                            'type': u'integer'},
                   u'uuid': {
                       'index': 'not_analyzed',
                       'store': 'yes',
                       'type': u'string'}}
        self.conn.indices.create_index(self.index_name)
        self.conn.indices.put_mapping(self.document_type, {'properties': mapping}, self.index_name)
        self.conn.index({"name": "Joe Tester", "parsedtext": "Joe Testere nice guy", "uuid": "11111", "position": 1},
                        self.index_name, self.document_type, 1)
        self.conn.index({"name": "Bill Baloney", "parsedtext": "Joe Testere nice guy", "uuid": "22222", "position": 2},
                        self.index_name, self.document_type, 2)
        self.conn.index({"value": "Joe Tester"}, self.index_name, self.document_type)
        self.conn.index({"value": 123343543536}, self.index_name, self.document_type)
        self.conn.index({"value": True}, self.index_name, self.document_type)
        self.conn.index({"value": 43.32}, self.index_name, self.document_type)
        # self.conn.index({"value": datetime.now()}, self.index_name, self.document_type)
        self.conn.indices.refresh(self.index_name)

    def test_TermQuery(self):
        q = TermQuery("name", "joe")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)

        q = TermQuery("name", "joe", 3)
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)

        q = TermQuery("name", "joe", "3")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)

        q = TermQuery("value", 43.32)
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)


if __name__ == "__main__":
    unittest.main()
