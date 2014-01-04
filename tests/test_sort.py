# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from pyes.tests import ESTestCase
from pyes.sort import SortFactory, SortOrder, GeoSortOrder, ScriptSortOrder
from pyes.query import Search, MatchAllQuery


class SortFactoryTestCase(unittest.TestCase):

    def test_sort_factory_empty(self):
        sort_factory = SortFactory()
        self.assertEqual(sort_factory.serialize(), None)

    def test_sort_factory_with_sort_order(self):
        sort_factory = SortFactory()
        sort_factory.add(SortOrder('foo'))
        self.assertEqual(sort_factory.serialize(), [{'foo': {}}])

    def test_sort_factory_reset(self):
        sort_factory = SortFactory()
        sort_factory.add(SortOrder('foo'))
        self.assertEqual(len(sort_factory.sort_orders), 1)
        sort_factory.reset()
        self.assertEqual(len(sort_factory.sort_orders), 0)


class SortOrderTestCase(unittest.TestCase):

    def test_sort_order_serialization(self):
        sort_order = SortOrder('foo')
        self.assertEqual(sort_order.serialize(), {'foo': {}})

    def test_sort_order_serialization_with_order(self):
        sort_order = SortOrder('foo', 'asc')
        self.assertEqual(sort_order.serialize(), {'foo': {'order': 'asc'}})

    def test_sort_order_serialization_with_missing(self):
        sort_order = SortOrder('foo', missing='_last')
        self.assertEqual(sort_order.serialize(), {'foo': {'missing': '_last'}})

    def test_sort_order_serialization_with_nested_path(self):
        sort_order = SortOrder('foo', mode='avg', nested_path='bar')
        self.assertEqual(
            sort_order.serialize(),
            {'foo': {'nested_path': 'bar', 'mode': 'avg'}}
        )


class GeoSortOrderTestCase(unittest.TestCase):

    def test_geo_sort_order_serialization(self):
        sort_order = GeoSortOrder(field='foo', lat=1, lon=1)
        self.assertEqual(
            sort_order.serialize(),
            {'_geo_distance': {'foo': [1, 1]}}
        )

    def test_geo_sort_order_serialization_with_unit(self):
        sort_order = GeoSortOrder(field='foo', lat=1, lon=1, unit='km')
        self.assertEqual(
            sort_order.serialize(),
            {'_geo_distance': {'foo': [1, 1], 'unit': 'km'}}
        )

    def test_geo_sort_order_serialization_with_order(self):
        sort_order = GeoSortOrder(field='foo', lat=1, lon=1, order='desc')
        self.assertEqual(
            sort_order.serialize(),
            {'_geo_distance': {'foo': [1, 1], 'order': 'desc'}}
        )

    def test_geo_sort_order_serialization_geohash(self):
        sort_order = GeoSortOrder(field='foo', geohash='drm3btev3e86')
        self.assertEqual(
            sort_order.serialize(),
            {'_geo_distance': {'foo': 'drm3btev3e86'}}
        )


class ScriptSortOrderTestCase(unittest.TestCase):

    def test_script_sort_order_serialization(self):
        sort_order = ScriptSortOrder("doc[foo].value + 1", type='number')
        self.assertEqual(
            sort_order.serialize(),
            {'_script': {'script': "doc[foo].value + 1", 'type': 'number'}}
        )


class SortOrderESTestCase(ESTestCase):

    def setUp(self):
        super(SortOrderESTestCase, self).setUp()
        self.conn.indices.create_index(self.index_name)
        #my es config has disabled automatic mapping creation
        mapping = {
            self.document_type: {
                'properties': {
                    'location': {
                        'type': 'geo_point'
                    }
                }
            }
        }
        self.conn.indices.put_mapping(self.document_type, mapping)
        self.conn.index(
            {'foo': 1, 'location': {'lat': 1, 'lon': 1}},
            self.index_name,
            self.document_type,
            1
        )
        self.conn.index(
            {'foo': 2, 'location': {'lat': 2, 'lon': 2}},
            self.index_name,
            self.document_type,
            2
        )
        self.conn.index(
            {'foo': 3, 'location': {'lat': 3, 'lon': 3}},
            self.index_name,
            self.document_type,
            3
        )

        self.conn.indices.refresh(self.index_name)

    def test_sorting_by_foo(self):
        search = Search(MatchAllQuery())
        search.sort.add(SortOrder('foo', order='desc'))
        resultset = self.conn.search(
            search,
            indices=self.index_name,
            doc_types=[self.document_type]
        )
        ids = [doc['_id'] for doc in resultset.hits]
        self.assertEqual(ids, ['3', '2', '1'])

    def test_sorting_by_script(self):
        search = Search(MatchAllQuery())
        search.sort.add(ScriptSortOrder("1.0/doc['foo'].value", type='number'))
        resultset = self.conn.search(
            search,
            indices=self.index_name,
            doc_types=[self.document_type]
        )
        ids = [doc['_id'] for doc in resultset.hits]
        self.assertEqual(ids, ['3', '2', '1'])

    def test_sorting_by_geolocation(self):
        search = Search(MatchAllQuery())
        search.sort.add(GeoSortOrder(field='location', lat=1, lon=1))
        resultset = self.conn.search(
            search,
            indices=self.index_name,
            doc_types=[self.document_type]
        )
        ids = [doc['_id'] for doc in resultset.hits]
        self.assertEqual(ids, ['1', '2', '3'])

if __name__ == "__main__":
    import unittest
    unittest.main()