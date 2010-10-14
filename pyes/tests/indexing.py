#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""
import unittest
from pyes.tests import ESTestCase
from pyes import TermQuery
from time import sleep

class IndexingTestCase(ESTestCase):
    def setUp(self):
        super(IndexingTestCase, self).setUp()
        self.conn.create_index("test-index")
        self.conn.delete_index("test-index2")

        #Sleep to allow ElasticSearch to set up 
        #mapping and indices before running tests
        #sleep(0.5)

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
        result = self.conn.index({"name":"Joe Tester"}, "test-index", "test-type", 1)
        self.assertResultContains(result, {'_type': 'test-type', '_id': '1', 'ok': True, '_index': 'test-index'} )

    def testIndexingWithoutID(self):
        """Testing an indexing given without ID"""
        result = self.conn.index({"name":"Joe Tester"}, "test-index", "test-type")
        self.assertResultContains(result, {'_type': 'test-type', 'ok': True, '_index': 'test-index'} )
        # should have an id of some value assigned.
        self.assertTrue(result.has_key('_id') and result['_id'])
        
    def testExplicitIndexCreate(self):
        """Creazione indice"""
        result = self.conn.delete_index("test-index2")
        result = self.conn.create_index("test-index2")
        self.assertResultContains(result, {'acknowledged': True, 'ok': True})
    
    def testDeleteByID(self):
        self.conn.index({"name":"Joe Tester"}, "test-index", "test-type", 1)
        self.conn.refresh(["test-index"])
        result = self.conn.delete("test-index", "test-type", 1)
        self.assertResultContains(result, {'_type': 'test-type', '_id': '1', 'ok': True, '_index': 'test-index'})
        
    def testDeleteIndex(self):
        self.conn.create_index("another-index")
        result = self.conn.delete_index("another-index")
        self.assertResultContains(result, {'acknowledged': True, 'ok': True})
        
    def testCannotCreateExistingIndex(self):
        self.conn.create_index("another-index")
        result = self.conn.create_index("another-index")
        self.conn.delete_index("another-index")
        self.assertResultContains(result, {'error': '[another-index] Already exists'})

    def testPutMapping(self):
        result = self.conn.create_index("test-index")        
        result = self.conn.put_mapping("test-type", {"test-type" : {"properties" : {"name" : {"type" : "string", "store" : "yes"}}}}, indexes=["test-index"])
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
        self.conn.index({"name":"Joe Tester"}, "test-index", "test-type", 1)
        self.conn.index({"name":"Bill Baloney"}, "test-index", "test-type", 2)
        self.conn.refresh(["test-index"])
        result = self.conn.get("test-index", "test-type", 1)
        self.assertResultContains(result, {'_type': 'test-type', '_id': '1', '_source': {'name': 'Joe Tester'}, '_index': 'test-index'})

    def testGetCountBySearch(self):
        self.conn.index({"name":"Joe Tester"}, "test-index", "test-type", 1)
        self.conn.index({"name":"Bill Baloney"}, "test-index", "test-type", 2)
        self.conn.refresh(["test-index"])
        q = TermQuery("name", "joe")
        result = self.conn.count(q, indexes=["test-index"])
        self.assertResultContains(result, {'count': 1})

#    def testSearchByField(self):
#        result = self.conn.search("name:joe")
#        self.assertResultContains(result, {'hits': {'hits': [{'_type': 'test-type', '_id': '1', '_source': {'name': 'Joe Tester'}, '_index': 'test-index'}], 'total': 1}})

#    def testTermsByField(self):
#        result = self.conn.terms(['name'])
#        self.assertResultContains(result, {'docs': {'max_doc': 2, 'num_docs': 2, 'deleted_docs': 0}, 'fields': {'name': {'terms': [{'term': 'baloney', 'doc_freq': 1}, {'term': 'bill', 'doc_freq': 1}, {'term': 'joe', 'doc_freq': 1}, {'term': 'tester', 'doc_freq': 1}]}}})
#        
#    def testTermsByIndex(self):
#        result = self.conn.terms(['name'], indexes=['test-index'])
#        self.assertResultContains(result, {'docs': {'max_doc': 2, 'num_docs': 2, 'deleted_docs': 0}, 'fields': {'name': {'terms': [{'term': 'baloney', 'doc_freq': 1}, {'term': 'bill', 'doc_freq': 1}, {'term': 'joe', 'doc_freq': 1}, {'term': 'tester', 'doc_freq': 1}]}}})
#
#    def testTermsMinFreq(self):
#        result = self.conn.terms(['name'], min_freq=2)
#        self.assertResultContains(result, {'docs': {'max_doc': 2, 'num_docs': 2, 'deleted_docs': 0}, 'fields': {'name': {'terms': []}}})
        
#    def testMLT(self):
#        self.conn.index({"name":"Joe Test"}, "test-index", "test-type", 3)
#        self.conn.refresh(["test-index"])
#        result = self.conn.morelikethis("test-index", "test-type", 1, ['name'], min_term_freq=1, min_doc_freq=1)
#        self.assertResultContains(result, {'hits': {'hits': [{'_type': 'test-type', '_id': '3', '_source': {'name': 'Joe Test'}, '_index': 'test-index'}], 'total': 1}})

if __name__ == "__main__":
    unittest.main()