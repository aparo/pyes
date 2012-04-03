# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from .estestcase import ESTestCase
from ..filters import TermFilter, NestedFilter
from ..query import FilteredQuery, MatchAllQuery, BoolQuery, TermQuery

class NestedSearchTestCase(ESTestCase):
    def setUp(self):
        super(NestedSearchTestCase, self).setUp()

        mapping = {
            'nested1': {
                'type': 'nested'
            }
        }
        self.conn.create_index(self.index_name)
        self.conn.put_mapping(self.document_type, {'properties': mapping}, self.index_name)
        self.conn.index({"field1": "value1",
                         "nested1": [{"n_field1": "n_value1_1",
                                      "n_field2": "n_value2_1"},
                                 {"n_field1": "n_value1_2",
                                  "n_field2": "n_value2_2"}]},
            self.index_name, self.document_type, 1)
        self.conn.index({"field1": "value1",
                         "nested1": [{"n_field1": "n_value1_1",
                                      "n_field2": "n_value2_2"},
                                 {"n_field1": "n_value1_2",
                                  "n_field2": "n_value2_1"}]},
            self.index_name, self.document_type, 2)
        self.conn.refresh(self.index_name)

    def test_nested_filter(self):
        q = FilteredQuery(MatchAllQuery(),
            TermFilter('_all', 'n_value1_1'))
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEquals(resultset.total, 2)

        q = FilteredQuery(MatchAllQuery(),
            TermFilter('nested1.n_field1', 'n_value1_1'))
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEquals(resultset.total, 0)

        q = FilteredQuery(MatchAllQuery(),
            TermFilter('nested1.n_field1', 'n_value1_1'))
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEquals(resultset.total, 0)

        q = FilteredQuery(MatchAllQuery(),
            NestedFilter('nested1',
                BoolQuery(must=[TermQuery('nested1.n_field1', 'n_value1_1')])))
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEquals(resultset.total, 2)

        q = FilteredQuery(MatchAllQuery(),
            NestedFilter('nested1',
                BoolQuery(must=[TermQuery('nested1.n_field1', 'n_value1_1'),
                                TermQuery('nested1.n_field2', 'n_value2_1')])))
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEquals(resultset.total, 1)


if __name__ == "__main__":
    unittest.main()

