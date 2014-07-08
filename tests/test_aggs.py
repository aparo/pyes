# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from pyes.tests import ESTestCase
from pyes.aggs import MissingAgg, MinAgg, MaxAgg

from pyes.query import MatchAllQuery

import datetime

class AggsSearchTestCase(ESTestCase):
    def setUp(self):

    	super(AggsSearchTestCase, self).setUp()
        mapping = {u'parsedtext': {'boost': 1.0,
                                   'index': 'analyzed',
                                   'store': 'yes',
                                   'type': u'string',
                                   "term_vector": "with_positions_offsets"},
                   u'name': {'boost': 1.0,
                             'index': 'analyzed',
                             'store': 'yes',
                             'type': u'string',
                             "term_vector": "with_positions_offsets"},
                   u'title': {'boost': 1.0,
                              'index': 'analyzed',
                              'store': 'yes',
                              'type': u'string',
                              "term_vector": "with_positions_offsets"},
                   u'position': {'store': 'yes',
                                 'type': u'integer'},
                   u'tag': {'store': 'yes',
                            'type': u'string'},
                   u'array': {'store': 'yes',
                            'type': u'integer'},
                   u'date': {'store': 'yes',
                             'type': u'date'},
                   u'uuid': {'boost': 1.0,
                             'index': 'not_analyzed',
                             'store': 'yes',
                             'type': u'string'}}
        self.conn.indices.create_index(self.index_name)
        self.conn.indices.put_mapping(self.document_type, {'properties': mapping}, self.index_name)
        self.conn.index({"name": "Joe Tester",
                         "parsedtext": "Joe Testere nice guy",
                         "uuid": "11111",
                         "position": 1,
                         "tag": "foo",
                         "integer": 1,
                         "date": datetime.date(2011, 5, 16)},
            self.index_name, self.document_type, 1)
        self.conn.index({"name": " Bill Baloney",
                         "parsedtext": "Bill Testere nice guy",
                         "uuid": "22222",
                         "position": 2,
                         "integer": 2,
                         "tag": "foo",
                         "date": datetime.date(2011, 4, 16)},
            self.index_name, self.document_type, 2)
        self.conn.index({"name": "Bill Clinton",
                         "parsedtext": "Bill is not nice guy",
                         "uuid": "33333",
                         "position": 3,
                         "tag": "bar",
                         "date": datetime.date(2011, 4, 28)},
            self.index_name, self.document_type, 3)
        self.conn.indices.refresh(self.index_name)

    def test_missing_agg(self):

        q = MatchAllQuery()
        q = q.search()
        missing = MissingAgg(name="missing", field="integer")
        q.agg.add(missing)
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)
        self.assertEqual(resultset.aggs.missing, {u'doc_count': 1})

    def test_min_agg(self):

        q = MatchAllQuery()
        q = q.search()
        missing = MinAgg(name="min", field="position")
        q.agg.add(missing)
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)
        self.assertEqual(resultset.aggs.min, {u'value': 1})

    def test_max_agg(self):

        q = MatchAllQuery()
        q = q.search()
        missing = MaxAgg(name="max", field="position")
        q.agg.add(missing)
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)
        self.assertEqual(resultset.aggs.max, {u'value': 3})

