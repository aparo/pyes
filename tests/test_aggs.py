# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from pyes.tests import ESTestCase
from pyes.aggs import MissingAgg, MinAgg, MaxAgg, NestedAgg, ReverseNestedAgg

from pyes.query import MatchAllQuery

import datetime

class AggsSearchTestCase(ESTestCase):
    def setUp(self):

    	super(AggsSearchTestCase, self).setUp()
        self.conn.indices.create_index(self.index_name)
        self.conn.indices.put_mapping(self.document_type, {'properties': self.get_default_mapping()}, self.index_name)
        self.conn.index({'name': 'Joe Tester',

                         'parsedtext': 'Joe Testere nice guy',
                         'uuid': '11111',
                         'position': 1,
                         'tag': 'foo',
                         'integer': 1,
                         'date': datetime.date(2011, 5, 16),
                         'resellers':[
                            {'name': 'name1', 'price': 100}, {'name': 'name1', 'price': 200}
                          ]
                         },
            self.index_name, self.document_type, 1)
        self.conn.index({'name': ' Bill Baloney',
                         'parsedtext': 'Bill Testere nice guy',
                         'uuid': '22222',
                         'position': 2,
                         'integer': 2,
                         'tag': 'foo',
                         'resellers':[],
                         'date': datetime.date(2011, 4, 16)},
            self.index_name, self.document_type, 2)
        self.conn.index({'name': 'Bill Clinton',
                         'parsedtext': 'Bill is not nice guy',
                         'uuid': '33333',
                         'position': 3,
                         'tag': 'bar',
                         'resellers':[
                            {'name': 'name1', 'price': 1000}, {'name': 'name1', 'price': 2000}
                          ],
                         'date': datetime.date(2011, 4, 28)},
            self.index_name, self.document_type, 3)
        self.conn.indices.refresh(self.index_name)

    def test_missing_agg(self):

        q = MatchAllQuery()
        q = q.search()
        missing = MissingAgg(name='missing', field='integer')
        q.agg.add(missing)
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)
        self.assertEqual(resultset.aggs.missing, {u'doc_count': 1})


    def test_min_agg(self):

        q = MatchAllQuery()
        q = q.search()
        min_agg = MinAgg(name='min', field='position')
        q.agg.add(min_agg)
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)
        self.assertEqual(resultset.aggs.min, {u'value': 1})

    def test_max_agg(self):

        q = MatchAllQuery()
        q = q.search()
        max_agg = MaxAgg(name='max', field='position')
        q.agg.add(max_agg)
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)
        self.assertEqual(resultset.aggs.max, {u'value': 3})

    def test_nested_agg(self):
        q = MatchAllQuery()
        q = q.search()
        nested = NestedAgg(name='nested', path='resellers')
        q.agg.add(nested)
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)
        self.assertEqual(resultset.aggs.nested, {u'doc_count': 4})

    def test_reverse_nested_agg(self):
        q = MatchAllQuery()
        q = q.search()
        reverse_nested = ReverseNestedAgg(name='reverse', field='id')
        nested = NestedAgg(name='nested', path='resellers', sub_aggs=[reverse_nested])

        q.agg.add(nested)
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)

        self.assertEqual(resultset.aggs.nested['doc_count'], 4)
        self.assertEqual(resultset.aggs.nested.reverse, {u'doc_count': 2})
