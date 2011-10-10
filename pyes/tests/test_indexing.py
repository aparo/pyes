#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""
import unittest
from pyes.tests import ESTestCase
from pyes import TermQuery
from pyes.exceptions import IndexAlreadyExistsException
from time import sleep

class IndexingTestCase(ESTestCase):
    def setUp(self):
        super(IndexingTestCase, self).setUp()
        self.conn.delete_index_if_exists(self.index_name)
        self.conn.delete_index_if_exists("test-index2")
        self.conn.delete_index_if_exists("another-index")
        self.conn.create_index(self.index_name)
        self.conn.create_index("test-index2")

    def tearDown(self):
        self.conn.delete_index_if_exists(self.index_name)
        self.conn.delete_index_if_exists("test-index2")
        self.conn.delete_index_if_exists("another-index")

    def testExists(self):
        self.assertTrue(self.conn.exists_index(self.index_name))
        self.assertFalse(self.conn.exists_index("test-index5"))

    def testCollectInfo(self):
        """
        Testing collecting server info
        """
        result = self.conn.collect_info()
        self.assertTrue(result.has_key('server'))
        self.assertTrue(result['server'].has_key('name'))
        self.assertTrue(result['server'].has_key('version'))

    def testIndexingWithID(self):
        """
        Testing an indexing given an ID
        """
        result = self.conn.index({"name":"Joe Tester"}, self.index_name, self.document_type, 1)
        self.assertResultContains(result, {'_type': 'test-type', '_id': '1', 'ok': True, '_index': 'test-index'})

    def testIndexingWithoutID(self):
        """Testing an indexing given without ID"""
        result = self.conn.index({"name":"Joe Tester"}, self.index_name, self.document_type)
        self.assertResultContains(result, {'_type': 'test-type', 'ok': True, '_index': 'test-index'})
        # should have an id of some value assigned.
        self.assertTrue(result.has_key('_id') and result['_id'])

    def testExplicitIndexCreate(self):
        """Creazione indice"""
        self.conn.delete_index("test-index2")
        result = self.conn.create_index("test-index2")
        self.assertResultContains(result, {'acknowledged': True, 'ok': True})

    def testDeleteByID(self):
        self.conn.index({"name":"Joe Tester"}, self.index_name, self.document_type, 1)
        self.conn.refresh(self.index_name)
        result = self.conn.delete(self.index_name, self.document_type, 1)
        self.assertResultContains(result, {'_type': 'test-type', '_id': '1', 'ok': True, '_index': 'test-index'})

    def testDeleteByIDWithEncoding(self):
        self.conn.index({"name":"Joe Tester"}, self.index_name, self.document_type, "http://hello/?#'there")
        self.conn.refresh(self.index_name)
        result = self.conn.delete(self.index_name, self.document_type, "http://hello/?#'there")
        self.assertResultContains(result, {'_type': 'test-type', '_id': 'http://hello/?#\'there', 'ok': True, '_index': 'test-index'})

    def testDeleteIndex(self):
        self.conn.create_index("another-index")
        result = self.conn.delete_index("another-index")
        self.assertResultContains(result, {'acknowledged': True, 'ok': True})

    def testCannotCreateExistingIndex(self):
        self.conn.create_index("another-index")
        self.assertRaises(IndexAlreadyExistsException, self.conn.create_index, "another-index")
        self.conn.delete_index("another-index")

    def testPutMapping(self):
        result = self.conn.put_mapping(self.document_type, {self.document_type : {"properties" : {"name" : {"type" : "string", "store" : "yes"}}}}, indices=self.index_name)
        self.assertResultContains(result, {'acknowledged': True, 'ok': True})

    def testIndexStatus(self):
        self.conn.create_index("another-index")
        result = self.conn.status(["another-index"])
        self.conn.delete_index("another-index")
        self.assertTrue(result.has_key('indices'))
        self.assertResultContains(result, {'ok': True})

    def testIndexFlush(self):
        self.conn.create_index("another-index")
        result = self.conn.flush(["another-index"])
        self.conn.delete_index("another-index")
        self.assertResultContains(result, {'ok': True})

    def testIndexRefresh(self):
        self.conn.create_index("another-index")
        result = self.conn.refresh(["another-index"])
        self.conn.delete_index("another-index")
        self.assertResultContains(result, {'ok': True})

    def testIndexOptimize(self):
        self.conn.create_index("another-index")
        result = self.conn.optimize(["another-index"])
        self.conn.delete_index("another-index")
        self.assertResultContains(result, {'ok': True})


    def testGetByID(self):
        self.conn.index({"name":"Joe Tester"}, self.index_name, self.document_type, 1)
        self.conn.index({"name":"Bill Baloney"}, self.index_name, self.document_type, 2)
        self.conn.refresh(self.index_name)
        result = self.conn.get(self.index_name, self.document_type, 1)
        self.assertResultContains(result, {'_type': 'test-type', '_id': '1', '_source': {'name': 'Joe Tester'}, '_index': 'test-index'})

    def testMultiGet(self):
        self.conn.index({"name":"Joe Tester"}, self.index_name, self.document_type, 1)
        self.conn.index({"name":"Bill Baloney"}, self.index_name, self.document_type, 2)
        self.conn.refresh(self.index_name)
        results = self.conn.mget(["1", "2"], self.index_name, self.document_type)
        self.assertEqual(len(results), 2)

    def testGetCountBySearch(self):
        self.conn.index({"name":"Joe Tester"}, self.index_name, self.document_type, 1)
        self.conn.index({"name":"Bill Baloney"}, self.index_name, self.document_type, 2)
        self.conn.refresh(self.index_name)
        q = TermQuery("name", "joe")
        result = self.conn.count(q, indices=self.index_name)
        self.assertResultContains(result, {'count': 1})


#    def testSearchByField(self):
#        resultset = self.conn.search("name:joe")
#        self.assertResultContains(result, {'hits': {'hits': [{'_type': 'test-type', '_id': '1', '_source': {'name': 'Joe Tester'}, '_index': 'test-index'}], 'total': 1}})

#    def testTermsByField(self):
#        result = self.conn.terms(['name'])
#        self.assertResultContains(result, {'docs': {'max_doc': 2, 'num_docs': 2, 'deleted_docs': 0}, 'fields': {'name': {'terms': [{'term': 'baloney', 'doc_freq': 1}, {'term': 'bill', 'doc_freq': 1}, {'term': 'joe', 'doc_freq': 1}, {'term': 'tester', 'doc_freq': 1}]}}})
#        
#    def testTermsByIndex(self):
#        result = self.conn.terms(['name'], indices=['test-index'])
#        self.assertResultContains(result, {'docs': {'max_doc': 2, 'num_docs': 2, 'deleted_docs': 0}, 'fields': {'name': {'terms': [{'term': 'baloney', 'doc_freq': 1}, {'term': 'bill', 'doc_freq': 1}, {'term': 'joe', 'doc_freq': 1}, {'term': 'tester', 'doc_freq': 1}]}}})
#
#    def testTermsMinFreq(self):
#        result = self.conn.terms(['name'], min_freq=2)
#        self.assertResultContains(result, {'docs': {'max_doc': 2, 'num_docs': 2, 'deleted_docs': 0}, 'fields': {'name': {'terms': []}}})

    def testMLT(self):
        self.conn.index({"name":"Joe Test"}, self.index_name, self.document_type, 1)
        self.conn.index({"name":"Joe Tester"}, self.index_name, self.document_type, 2)
        self.conn.index({"name":"Joe Tested"}, self.index_name, self.document_type, 3)
        self.conn.refresh(self.index_name)
        sleep(0.5)
        result = self.conn.morelikethis(self.index_name, self.document_type, 1, ['name'], min_term_freq=1, min_doc_freq=1)
        del result[u'took']
        self.assertResultContains(result, {u'_shards': {u'successful': 5, u'failed': 0, u'total': 5}})
        self.assertTrue(u'hits' in result)
        self.assertResultContains(result['hits'], {u'hits': [
                                  {u'_score': 0.19178301, u'_type': u'test-type', u'_id': u'3', u'_source': {u'name': u'Joe Tested'}, u'_index': u'test-index', u'_version': 1},
                                  {u'_score': 0.19178301, u'_type': u'test-type', u'_id': u'2', u'_source': {u'name': u'Joe Tester'}, u'_index': u'test-index', u'_version': 1}
                                  ], u'total': 2, u'max_score': 0.19178301})

    def testVersion(self):
        self.conn.index({"name":"Joe Test"}, self.index_name, self.document_type, 1, force_insert=True)
        self.assertRaises(DocumentAlreadyExistsEngineException,
                          self.conn.index,
                          *({"name":"Joe Test2"}, self.index_name, self.document_type, 1), **{"force_insert":True})
        self.conn.index({"name":"Joe Test"}, self.index_name, self.document_type, 1, version=1)
        self.conn.index({"name":"Joe Test"}, self.index_name, self.document_type, 1, version=2)
        self.assertRaises(VersionConflictEngineException,
                          self.conn.index,
                          *({"name":"Joe Test2"}, self.index_name, self.document_type, 1), **{"version":2})
        item = self.conn.get(self.index_name, self.document_type, 1)
        self.assertEqual(item["_version"], 3)
        self.assertEqual(item._version, 3)

if __name__ == "__main__":
    unittest.main()
