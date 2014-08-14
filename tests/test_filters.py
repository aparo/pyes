# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
import datetime


from pyes.tests import ESTestCase
from pyes import filters, Search, utils


class ScriptFilterTestCase(ESTestCase):

    def test_lang(self):
        f = filters.ScriptFilter(
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


class FilterTests(ESTestCase):
    def setUp(self):
        super(FilterTests, self).setUp()
        mapping = {
            "name": {"type": "string"},
            "nested_filter": {
                "type": "nested",
                "properties": {
                    "key_1": {"type": "integer", "index": "not_analyzed"},
                    "key_2": {"type": "integer", "index": "not_analyzed"}
                }
            },
            "terms_filter": {
                "type": "integer"
            },
            "exists_filter": {
                "type": "string"
            },

        }
        self.conn.indices.create_index(self.index_name)
        self.conn.indices.put_mapping(self.document_type,
                                      {'properties': mapping}, self.index_name)
        self.conn.index(
            {
                "name": "1",
                "nested_filter": [
                    {
                        "key_1": [1, 100],
                        "key_2": [3]
                    },
                    {
                        "key_1": [2],
                        "key_2": [4]
                    }
                ],
                "terms_filter": 25,
                "exists_filter": "something"
            },
            self.index_name, self.document_type, 1)
        self.conn.index(
            {
                "name": "2",
                "nested_filter": [
                    {
                        "key_1": [1, 2, 200],
                        "key_2": [3, 5]
                    }
                ],
                "terms_filter": 24,
            },
            self.index_name, self.document_type, 2)

        self.internal_type = "test-type2"
        self.conn.indices.put_mapping(self.internal_type,
                                      {'properties': mapping}, self.index_name)
        self.conn.index({"name": "4"},
                        self.index_name, self.internal_type, 4)
        self.conn.indices.refresh(self.index_name)


class IdsFilterTestCase(FilterTests):

    def test_ids_direct_type(self):
        """Doc type set in search """
        f = filters.IdsFilter(values=[1, 2, 4])
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(2, len(result.hits))
        self.assertItemsEqual([u'1', u'2'], [item._id for item in result.hits])

    def test_ids_filter_with_type(self):
        """Doc type set in filter and left blank in search """
        f = filters.IdsFilter(values=[1, 2, 4], type=self.internal_type)
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[])
        self.assertEqual(1, len(result.hits))
        self.assertItemsEqual([u'4'], [item._id for item in result.hits])


class NestedFilterTestCase(FilterTests):

    def test_nested_filter_1(self):
        filter_list = filters.TermFilter("key_1", 1)
        f = filters.NestedFilter(path="nested_filter", filter=filter_list)
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(2, len(result.hits))

        filter_list = filters.TermFilter("key_1", 200)
        f = filters.NestedFilter(path="nested_filter", filter=filter_list)
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(1, len(result.hits))
        self.assertEqual(u'2', result.hits[0]['_id'])

    def test_nested_filter_2(self):
        f1 = filters.TermFilter("key_1", 1)
        f2 = filters.TermFilter("key_2", 3)
        filter_list = filters.ANDFilter([f1, f2])
        f = filters.NestedFilter(path="nested_filter", filter=filter_list)
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(2, len(result.hits))

        f1 = filters.TermFilter("key_1", 1)
        f2 = filters.TermFilter("key_2", 4)
        filter_list = filters.ANDFilter([f1, f2])
        f = filters.NestedFilter(path="nested_filter", filter=filter_list)
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(0, len(result.hits))

        f1 = filters.TermFilter("key_1", 2)
        f2 = filters.TermFilter("key_2", 4)
        filter_list = filters.ANDFilter([f1, f2])
        f = filters.NestedFilter(path="nested_filter", filter=filter_list)
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(1, len(result.hits))


class TermsFilterTestCase(FilterTests):
    def test_terms_filter_1(self):
        """Without execution set"""
        f = filters.TermsFilter(values=[24], field='terms_filter')
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(1, len(result.hits))

        f = filters.TermsFilter(values=[24, 25], field='terms_filter')
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(2, len(result.hits))

        f = filters.TermsFilter(values=[26], field='terms_filter')
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(0, len(result.hits))

    def test_terms_filter_2(self):
        """With execution set"""
        f = filters.TermsFilter(values=[24], field='terms_filter')
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(1, len(result.hits))

        f = filters.TermsFilter(values=[24, 25], field='terms_filter')
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(2, len(result.hits))

        f = filters.TermsFilter(values=[26], field='terms_filter')
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(0, len(result.hits))


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
        self.conn.indices.put_mapping(self.document_type,
                                      {'properties': mapping},
                                      self.index_name)
        self.conn.index({'date': datetime.date(2011, 5, 16), 'value': 10},
                        self.index_name, self.document_type, 1)
        self.conn.index({'value': 100, 'date': datetime.date(2011, 4, 16)},
                        self.index_name, self.document_type, 2)
        self.conn.index({'value': 99, 'date': datetime.date(2011, 4, 28)},
                        self.index_name, self.document_type, 3)
        self.conn.indices.refresh(self.index_name)

    def search(self, qrange):
        f = filters.RangeFilter(qrange)
        q = Search(filter=f)
        return self.conn.search(query=q, indices=self.index_name,
                                doc_types=[self.document_type])

    def test_upper_bound(self):
        qrange = utils.ESRange(field="value", from_value=10, to_value=100,
                               include_lower=None, include_upper=False)
        result = self.search(qrange)
        self.assertEqual(1, len(result.hits))

        qrange = utils.ESRange(field="value", from_value=10, to_value=100,
                               include_lower=None, include_upper=True)
        result = self.search(qrange)
        self.assertEqual(2, len(result.hits))

    def test_lower_bound(self):
        qrange = utils.ESRange(field="value", from_value=10, to_value=1000,
                               include_lower=False, include_upper=None)
        result = self.search(qrange)
        self.assertEqual(2, len(result.hits))

        qrange = utils.ESRange(field="value", from_value=10, to_value=1000,
                               include_lower=True, include_upper=None)
        result = self.search(qrange)
        self.assertEqual(3, len(result.hits))

    def test_lower_none(self):
        qrange = utils.ESRange(field="value", from_value=None, to_value=11,
                               include_lower=None, include_upper=None)
        result = self.search(qrange)
        self.assertEqual(1, len(result.hits))

    def test_upper_none(self):
        qrange = utils.ESRange(field="value", from_value=98.0, to_value=None,
                               include_lower=None, include_upper=None)
        result = self.search(qrange)
        self.assertEqual(2, len(result.hits))


class TermsLookupTestCase(FilterTests):

    def test_filter(self):
        tl = utils.TermsLookup(index=self.index_name, type=self.document_type,
                               id=1, path='terms_lookup_filter')
        f = filters.TermsFilter('terms_filter', tl)
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(2, len(result.hits))

        tl = utils.TermsLookup(index=self.index_name, type=self.document_type,
                               id=2, path='terms_lookup_filter')
        f = filters.TermsFilter('terms_filter', tl)
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(1, len(result.hits))


class ExistsFilterTestCase(FilterTests):
    def test_exists(self):
        f = filters.ExistsFilter(field='exists_filter')
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[self.document_type])
        self.assertEqual(1, len(result.hits))
        self.assertEqual(u'1', result.hits[0]['_id'])


class TypeFilterTestCase(FilterTests):

    def test_type(self):
        f = filters.TypeFilter(type=self.document_type)
        q = Search(filter=f)
        print self.dump(q.serialize())
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[])
        self.assertEqual(2, len(result.hits))
        print result.hits
        self.assertItemsEqual([u'1', u'2'], [item._id for item in result.hits])

        f = filters.TypeFilter(type=self.internal_type)
        q = Search(filter=f)
        result = self.conn.search(query=q, indices=self.index_name,
                                  doc_types=[])
        self.assertEqual(1, len(result.hits))
        self.assertItemsEqual([u'4'], [item._id for item in result.hits])

if __name__ == "__main__":
    unittest.main()
