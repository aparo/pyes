# -*- coding: utf-8 -*-
from __future__ import absolute_import
from .estestcase import ESTestCase
from ..query import TermQuery
from ..es import _raise_exception_if_bulk_item_failed, _is_bulk_item_ok
from ..exceptions import BulkOperationException

class BulkTestCase(ESTestCase):
    def setUp(self):
        super(BulkTestCase, self).setUp()
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
                   u'pos': {'store': 'yes',
                            'type': u'integer'},
                   u'uuid': {'boost': 1.0,
                             'index': 'not_analyzed',
                             'store': 'yes',
                             'type': u'string'}}
        self.conn.create_index(self.index_name)
        self.conn.put_mapping(self.document_type, {'properties': mapping}, self.index_name)

    def test_force(self):
        self.conn.raise_on_bulk_item_failure = False
        self.conn.index({"name": "Joe Tester", "parsedtext": "Joe Testere nice guy", "uuid": "11111", "position": 1},
            self.index_name, self.document_type, 1, bulk=True)
        self.conn.index({"name": "Bill Baloney", "parsedtext": "Bill Testere nice guy", "uuid": "22222", "position": 2},
            self.index_name, self.document_type, 2, bulk=True)
        self.conn.index({"name": "Bill Clinton", "parsedtext": """Bill is not
                nice guy""", "uuid": "33333", "position": 3}, self.index_name, self.document_type, 3, bulk=True)
        bulk_result = self.conn.force_bulk()
        self.assertEquals(len(bulk_result['items']), 3)
        self.conn.refresh(self.index_name)
        q = TermQuery("name", "bill")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 2)

    def test_automatic_flush(self):
        self.conn.force_bulk()
        self.conn.bulk_size = 3
        self.conn.raise_on_bulk_item_failure = False

        self.assertIsNone(
            self.conn.index({"name": "Joe Tester", "parsedtext": "Joe Testere nice guy", "uuid": "11111", "position": 1}
                ,
                self.index_name, self.document_type, 4, bulk=True))
        self.assertIsNone(self.conn.flush_bulk(False))
        self.assertEqual(len(self.conn.bulker.bulk_data), 1)

        self.assertIsNone(
            self.conn.index(
                    {"name": "Bill Baloney", "parsedtext": "Bill Testere nice guy", "uuid": "22222", "position": 2},
                self.index_name, self.document_type, 5, bulk=True))
        self.assertIsNone(self.conn.flush_bulk(False))
        self.assertEqual(len(self.conn.bulker.bulk_data), 2)

        bulk_result = self.conn.index(
                {"name": "Bill Clinton", "parsedtext": """Bill is not nice guy""", "uuid": "33333", "position": 3},
            self.index_name, self.document_type, 6, bulk=True)
        self.assertEquals(len(bulk_result['items']), 3)
        self.assertEqual(self.conn.bulker.bulk_data, [])

        self.conn.bulk_size = 3

        self.assertIsNone(self.conn.delete(self.index_name, self.document_type, 4, True))
        self.assertIsNone(self.conn.flush_bulk(False))
        self.assertEqual(len(self.conn.bulker.bulk_data), 1)

        self.assertIsNone(self.conn.delete(self.index_name, self.document_type, 5, True))
        self.assertIsNone(self.conn.flush_bulk(False))
        self.assertEqual(len(self.conn.bulker.bulk_data), 2)

        bulk_result = self.conn.delete(self.index_name, self.document_type, 6, True)
        self.assertIsNone(self.conn.flush_bulk(False))
        self.assertEquals(len(bulk_result['items']), 3)
        self.assertEqual(self.conn.bulker.bulk_data, [])

        self.conn.refresh(self.index_name)

    def test_error(self):
        self.conn.force_bulk()
        self.conn.bulk_size = 2

        self.assertIsNone(
            self.conn.index(
                    {"name": "Bill Baloney", "parsedtext": "Bill Testere nice guy", "uuid": "22222", "position": 2},
                self.index_name, self.document_type, 7, bulk=True))
        self.assertIsNone(self.conn.flush_bulk(False))
        self.assertEqual(len(self.conn.bulker.bulk_data), 1)

        bulk_result = self.conn.index(
            "invalid", self.index_name, self.document_type, 8, bulk=True)
        self.assertEquals(len(bulk_result['items']), 2)
        self.assertTrue(bulk_result["items"][0]["index"]["ok"])
        self.assertTrue("error" in bulk_result["items"][1]["index"])
        self.assertEqual(self.conn.bulker.bulk_data, [])

        self.conn.bulk_size = 2
        self.assertIsNone(self.conn.delete(
            self.index_name, self.document_type, 9, bulk=True))
        bulk_result = self.conn.delete(
            self.index_name, "#foo", 9, bulk=True)
        self.assertEquals(len(bulk_result['items']), 2)
        self.assertTrue(bulk_result["items"][0]["delete"]["ok"])
        self.assertTrue("error" in bulk_result["items"][1]["delete"])
        self.assertEqual(self.conn.bulker.bulk_data, [])

    def test_raise_exception_if_bulk_item_failed(self):
        index_ok_1 = {'index': {'_type': 'test-type', '_id': '4', 'ok': True, '_version': 1, '_index': 'test-index'}}
        self.assertTrue(_is_bulk_item_ok(index_ok_1))
        index_ok_2 = {'index': {'_type': 'test-type', '_id': '5', 'ok': True, '_version': 1, '_index': 'test-index'}}
        self.assertTrue(_is_bulk_item_ok(index_ok_2))
        index_ok_3 = {'index': {'_type': 'test-type', '_id': '6', 'ok': True, '_version': 1, '_index': 'test-index'}}
        self.assertTrue(_is_bulk_item_ok(index_ok_3))

        index_error_1 = {'index': {'_type': 'test-type', '_id': '8', '_index': 'test-index',
                                   'error': 'ElasticSearchParseException[Failed to derive xcontent from (offset=0, length=7): [105, 110, 118, 97, 108, 105, 100]]'}}
        self.assertFalse(_is_bulk_item_ok(index_error_1))
        index_error_2 = {'index': {'_type': 'test-type', '_id': '9', '_index': 'test-index',
                                   'error': 'ElasticSearchParseException[Failed to derive xcontent from (offset=0, length=7): [105, 110, 118, 97, 108, 105, 100]]'}}
        self.assertFalse(_is_bulk_item_ok(index_error_2))

        delete_ok_1 = {'delete': {'_type': 'test-type', '_id': '4', 'ok': True, '_version': 2, '_index': 'test-index'}}
        self.assertTrue(_is_bulk_item_ok(delete_ok_1))
        delete_ok_2 = {'delete': {'_type': 'test-type', '_id': '5', 'ok': True, '_version': 2, '_index': 'test-index'}}
        self.assertTrue(_is_bulk_item_ok(delete_ok_2))
        delete_ok_3 = {'delete': {'_type': 'test-type', '_id': '6', 'ok': True, '_version': 2, '_index': 'test-index'}}
        self.assertTrue(_is_bulk_item_ok(delete_ok_3))
        delete_error_1 = {'delete': {'_type': '#foo', '_id': '9', '_index': 'test-index',
                                     'error': "InvalidTypeNameException[mapping type name [#foo] should not include '#' in it]"}}
        self.assertFalse(_is_bulk_item_ok(delete_error_1))
        delete_error_2 = {'delete': {'_type': '#foo', '_id': '10', '_index': 'test-index',
                                     'error': "InvalidTypeNameException[mapping type name [#foo] should not include '#' in it]"}}
        self.assertFalse(_is_bulk_item_ok(delete_error_1))

        index_all_ok = {'items': [
            index_ok_1,
            index_ok_2,
            index_ok_3],
                        'took': 4}
        delete_all_ok = {'items': [
            delete_ok_1,
            delete_ok_2,
            delete_ok_3],
                         'took': 0}
        index_one_error = {'items': [
            index_ok_1,
            index_error_1],
                           'took': 156}
        index_two_errors = {'items': [
            index_ok_2,
            index_error_1,
            index_error_2],
                            'took': 156}
        delete_one_error = {'items': [
            delete_ok_1,
            delete_error_1],
                            'took': 1}
        delete_two_errors = {'items': [
            delete_ok_2,
            delete_error_1,
            delete_error_2],
                             'took': 1}
        mixed_errors = {'items': [
            delete_ok_3,
            index_ok_1,
            index_error_1,
            delete_error_1,
            delete_error_2],
                        'took': 1}
        oops_all_errors = {'items': [
            index_error_1,
            delete_error_1,
            delete_error_2],
                           'took': 1}

        self.assertIsNone(_raise_exception_if_bulk_item_failed(index_all_ok))
        self.assertIsNone(_raise_exception_if_bulk_item_failed(delete_all_ok))

        with self.assertRaises(BulkOperationException) as cm:
            _raise_exception_if_bulk_item_failed(index_one_error)
        self.assertEquals(cm.exception, BulkOperationException(
            [index_error_1], index_one_error))

        with self.assertRaises(BulkOperationException) as cm:
            _raise_exception_if_bulk_item_failed(index_two_errors)
        self.assertEquals(cm.exception, BulkOperationException(
            [index_error_1, index_error_2], index_two_errors))

        with self.assertRaises(BulkOperationException) as cm:
            _raise_exception_if_bulk_item_failed(delete_one_error)
        self.assertEquals(cm.exception, BulkOperationException(
            [delete_error_1], delete_one_error))

        with self.assertRaises(BulkOperationException) as cm:
            _raise_exception_if_bulk_item_failed(delete_two_errors)
        self.assertEquals(cm.exception, BulkOperationException(
            [delete_error_1, delete_error_2], delete_two_errors))

        with self.assertRaises(BulkOperationException) as cm:
            _raise_exception_if_bulk_item_failed(mixed_errors)
        self.assertEquals(cm.exception, BulkOperationException(
            [index_error_1, delete_error_1, delete_error_2], mixed_errors))

        with self.assertRaises(BulkOperationException) as cm:
            _raise_exception_if_bulk_item_failed(oops_all_errors)
        self.assertEquals(cm.exception, BulkOperationException(
            [index_error_1, delete_error_1, delete_error_2], oops_all_errors))

        # now, try it against a real index...
        self.conn.force_bulk()
        self.conn.raise_on_bulk_item_failure = False
        self.conn.bulk_size = 1

        bulk_result = self.conn.delete(self.index_name, "#bogus", 9, bulk=True)
        self.assertFalse(_is_bulk_item_ok(bulk_result["items"][0]))

        bulk_result = self.conn.index("invalid", self.index_name, self.document_type, 8, bulk=True)
        self.assertFalse(_is_bulk_item_ok(bulk_result["items"][0]))

        self.conn.raise_on_bulk_item_failure = True

        with self.assertRaises(BulkOperationException) as cm:
            self.conn.delete(
                self.index_name, "#bogus", 9, bulk=True)

        with self.assertRaises(BulkOperationException) as cm:
            self.conn.index(
                "invalid", self.index_name, self.document_type, 8, bulk=True)
