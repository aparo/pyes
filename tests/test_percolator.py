# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from pyes.tests import ESTestCase
from pyes.query import *
import unittest

class PercolatorTestCase(ESTestCase):
    def setUp(self):
        super(PercolatorTestCase, self).setUp()
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
        self.conn.indices.create_index(self.index_name)
        self.conn.indices.put_mapping(self.document_type, {'properties':mapping}, self.index_name)
        self.conn.create_percolator(
            'test-index',
            'test-perc1',
            QueryStringQuery(query='apple', search_fields='_all')
        )
        self.conn.create_percolator(
            'test-index',
            'test-perc2',
            QueryStringQuery(query='apple OR iphone', search_fields='_all')
        )
        self.conn.create_percolator(
            'test-index',
            'test-perc3',
            QueryStringQuery(query='apple AND iphone', search_fields='_all')
        )
        self.conn.indices.refresh(self.index_name)

    def test_percolator(self):
        results = self.conn.percolate('test-index', 'test-type', PercolatorQuery({'name': 'iphone'}))
        self.assertTrue({'_id': 'test-perc1', '_index': 'test-index'} not in results['matches'])
        self.assertTrue({'_id': 'test-perc2','_index': 'test-index'} in results['matches'])
        self.assertTrue({'_id': 'test-perc3', '_index': 'test-index'} not in results['matches'])

    def test_or(self):
        results = self.conn.percolate('test-index', 'test-type', PercolatorQuery({'name': 'apple'}))
        self.assertTrue({'_id': 'test-perc1', '_index': 'test-index'} in results['matches'])
        self.assertTrue({'_id': 'test-perc2', '_index': 'test-index'} in results['matches'])
        self.assertTrue({'_id': 'test-perc3', '_index': 'test-index'} not in results['matches'])

    def test_and(self):
        results = self.conn.percolate('test-index', 'test-type', PercolatorQuery({'name': 'apple iphone'}))
        self.assertTrue({'_id': 'test-perc1', '_index': 'test-index'} in results['matches'])
        self.assertTrue({'_id': 'test-perc2', '_index': 'test-index'} in results['matches'])
        self.assertTrue({'_id': 'test-perc3', '_index': 'test-index'} in results['matches'])

    def tearDown(self):
        self.conn.delete_percolator('test-index', 'test-perc1')
        self.conn.delete_percolator('test-index', 'test-perc2')
        self.conn.delete_percolator('test-index', 'test-perc3')
        super(PercolatorTestCase, self).tearDown()


if __name__ == "__main__":
    unittest.main()
