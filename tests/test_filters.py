# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
import datetime


from pyes.tests import ESTestCase
from pyes.filters import ScriptFilter, RangeFilter
from pyes.utils import ESRange
from pyes.es import Search

class ScriptFilterTestCase(ESTestCase):

    def test_lang(self):
        f = ScriptFilter(
            'name',
            params={
                'param_1': 1,
                'param_2': 'boo',
            },
            lang='native'
        )
        expected = {
            'script': {
                'params': {
                    'param_1': 1,
                    'param_2': 'boo'},
                'script': 'name',
                'lang': 'native',
            }
        }
        self.assertEqual(expected, f.serialize())

class RangeFilterTestCase(ESTestCase):

    def setUp(self):

        super(RangeFilterTestCase, self).setUp()
        mapping = {
                   u'value': {'store': 'yes',
                            'type': u'integer'},
                   u'date': {'store': 'yes',
                             'type': u'date'},
                  }
        self.conn.indices.create_index(self.index_name)
        self.conn.indices.put_mapping(self.document_type, {'properties': mapping}, self.index_name)
        self.conn.index({
                         'date': datetime.date(2011, 5, 16),
                         'value': 10
                         },
            self.index_name, self.document_type, 1)
        self.conn.index({'value': 100,
                         'date': datetime.date(2011, 4, 16)},
            self.index_name, self.document_type, 2)
        self.conn.index({'value': 99,
                         'date': datetime.date(2011, 4, 28)},
            self.index_name, self.document_type, 3)
        self.conn.indices.refresh(self.index_name)

    def search(self, qrange):
        f = RangeFilter(qrange)
        q = Search(filter=f)
        print q.serialize()
        return self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])

    def test_upper_bound(self):
        qrange = ESRange(field="value", from_value=10, to_value=100, include_lower=None,
                         include_upper=False)
        result = self.search(qrange)
        self.assertEqual(1, len(result.hits))

        qrange = ESRange(field="value", from_value=10, to_value=100, include_lower=None,
                         include_upper=True)
        result = self.search(qrange)
        self.assertEqual(2, len(result.hits))

    def test_lower_bound(self):
        qrange = ESRange(field="value", from_value=10, to_value=1000, include_lower=False,
                         include_upper=None)
        result = self.search(qrange)
        self.assertEqual(2, len(result.hits))

        qrange = ESRange(field="value", from_value=10, to_value=1000, include_lower=True,
                         include_upper=None)
        result = self.search(qrange)
        self.assertEqual(3, len(result.hits))

    def test_lower_none(self):
        qrange = ESRange(field="value", from_value=None, to_value=11, include_lower=None,
                         include_upper=None)
        result = self.search(qrange)
        self.assertEqual(1, len(result.hits))


    def test_upper_none(self):
        qrange = ESRange(field="value", from_value=98.0, to_value=None, include_lower=None,
                         include_upper=None)
        result = self.search(qrange)
        print result.hits
        self.assertEqual(2, len(result.hits))


if __name__ == "__main__":
    unittest.main()
