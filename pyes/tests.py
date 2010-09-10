#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyelasticsearch.  These require an elasticsearch server running on the default port (localhost:9200).
"""
import unittest
from elasticsearch import ElasticSearch
from query import *
from pprint import pprint

class ElasticSearchTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = ElasticSearch('http://127.0.0.1:9200/')
        self.conn.delete_index("test-index")
        
    def tearDown(self):
        self.conn.delete_index("test-index")

    def assertResultContains(self, result, expected):
        for (key, value) in expected.items():
            self.assertEquals(value, result[key])

class IndexingTestCase(ElasticSearchTestCase):
        
    def testIndexingWithID(self):
        result = self.conn.index({"name":"Joe Tester"}, "test-index", "test-type", 1)
        self.assertResultContains(result, {'_type': 'test-type', '_id': '1', 'ok': True, '_index': 'test-index'} )

    def testIndexingWithoutID(self):
        result = self.conn.index({"name":"Joe Tester"}, "test-index", "test-type")
        self.assertResultContains(result, {'_type': 'test-type', 'ok': True, '_index': 'test-index'} )
        # should have an id of some value assigned.
        self.assertTrue(result.has_key('_id') and result['_id'])
        
    def testExplicitIndexCreate(self):
        result = self.conn.create_index("test-index")
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

                
class SearchTestCase(ElasticSearchTestCase):
    def setUp(self):
        super(SearchTestCase, self).setUp()
        self.conn.index({"name":"Joe Tester"}, "test-index", "test-type", 1)
        self.conn.index({"name":"Bill Baloney"}, "test-index", "test-type", 2)
        self.conn.refresh(["test-index"])
    
    def testGetByID(self):
        result = self.conn.get("test-index", "test-type", 1)
        self.assertResultContains(result, {'_type': 'test-type', '_id': '1', '_source': {'name': 'Joe Tester'}, '_index': 'test-index'})

    def testGetCountBySearch(self):
        result = self.conn.count("name:joe")
        self.assertResultContains(result, {'count': 1})

    def testSearchByField(self):
        result = self.conn.search("name:joe")
        self.assertResultContains(result, {'hits': {'hits': [{'_type': 'test-type', '_id': '1', '_source': {'name': 'Joe Tester'}, '_index': 'test-index'}], 'total': 1}})

    def testTermsByField(self):
        result = self.conn.terms(['name'])
        self.assertResultContains(result, {'docs': {'max_doc': 2, 'num_docs': 2, 'deleted_docs': 0}, 'fields': {'name': {'terms': [{'term': 'baloney', 'doc_freq': 1}, {'term': 'bill', 'doc_freq': 1}, {'term': 'joe', 'doc_freq': 1}, {'term': 'tester', 'doc_freq': 1}]}}})
        
    def testTermsByIndex(self):
        result = self.conn.terms(['name'], indexes=['test-index'])
        self.assertResultContains(result, {'docs': {'max_doc': 2, 'num_docs': 2, 'deleted_docs': 0}, 'fields': {'name': {'terms': [{'term': 'baloney', 'doc_freq': 1}, {'term': 'bill', 'doc_freq': 1}, {'term': 'joe', 'doc_freq': 1}, {'term': 'tester', 'doc_freq': 1}]}}})

    def testTermsMinFreq(self):
        result = self.conn.terms(['name'], min_freq=2)
        self.assertResultContains(result, {'docs': {'max_doc': 2, 'num_docs': 2, 'deleted_docs': 0}, 'fields': {'name': {'terms': []}}})
        
    def testMLT(self):
        self.conn.index({"name":"Joe Test"}, "test-index", "test-type", 3)
        self.conn.refresh(["test-index"])
        result = self.conn.morelikethis("test-index", "test-type", 1, ['name'], min_term_freq=1, min_doc_freq=1)
        self.assertResultContains(result, {'hits': {'hits': [{'_type': 'test-type', '_id': '3', '_source': {'name': 'Joe Test'}, '_index': 'test-index'}], 'total': 1}})

class TestFileSaveTestCase(ElasticSearchTestCase):
    def test_filesave(self):
        mapping = {
                   "my_attachment" : { "type" : "attachment", 
                                      'fields':{
                                        "file" : {'store' : "yes"},
                                        "date" : {'store' : "yes"},
                                        "author" : {'store': "yes"},
                                        "title" : {'store': "yes"},}
                                      }
                   }
        self.conn.create_index("test-index")
        self.conn.put_mapping("test-type", {"test-type":{'properties':mapping}}, ["test-index"])
        self.conn.refresh(["test-index"])
        self.conn.get_mapping("test-type", ["test-index"])
#        name = "/Users/alberto/Documents/workspace/elasticsearch/plugins/mapper/attachments/src/test/java/org/elasticsearch/index/mapper/xcontent/testXHTML.html"
        name = "test.py"
        content = open(name, "rb").read()
        self.conn.put_file(name, "test-index", "test-type", 1)
        self.conn.refresh(["test-index"])
        self.conn.get_mapping("test-type", ["test-index"])
        nname, ncontent = self.conn.get_file("test-index", "test-type", 1)
        self.assertEquals(name, nname)
        self.assertEquals(content, ncontent)

class QueryAttachmentTestCase(ElasticSearchTestCase):
    def setUp(self):
        super(QueryAttachmentTestCase, self).setUp()
        mapping = {
                   "my_attachment" : { "type" : "attachment", 
                                      'fields':{
                                        "file" : {'store' : "yes"},
                                        "date" : {'store' : "yes"},
                                        "author" : {'store': "yes"},
                                        "title" : {'store': "yes"},}
                                      },
                   'uuid': {'boost': 1.0,
                           'index': 'not_analyzed',
                           'store': 'yes',
                           'type': u'string'}
                   }
        self.conn.debug_dump=True
        self.conn.create_index("test-index")
        self.conn.put_mapping("test-type", {"test-type":{'properties':mapping}}, ["test-index"])
        self.conn.refresh(["test-index"])
        self.conn.get_mapping("test-type", ["test-index"])
#        self.conn.index({"my_attachment":file_to_attachment("/opt/brainaetic/rd2/brainaetic/data/mediatest/programma.doc"), "uuid":"1" }, "test-index", "test-type", 1)
        self.conn.index({"my_attachment":file_to_attachment("/Users/alberto/Documents/workspace/elasticsearch/plugins/mapper/attachments/src/test/java/org/elasticsearch/index/mapper/xcontent/testXHTML.html"), "uuid":"1" }, "test-index", "test-type", 1)
#        dirname = "/opt/brainaetic/data/mediatest/"
#        for pos, filename in enumerate(os.listdir(dirname)):
#            filename = os.path.join(dirname, filename)
#            if os.path.isfile(filename):
#                self.conn.index({"my_attachment":file_to_attachment(filename), "uuid":str(pos+1) }, "test-index", "test-type", pos+1)
#                print str(pos+1)
#                break
        self.conn.refresh(["test-index"])
        print "-"*80, "After index"
        self.conn.get_mapping("test-type", ["test-index"])

    def test_TermQuery(self):
        q = TermQuery("uuid", "1")
        result = self.conn.search(query = q)
        pprint(result)
        self.assertEquals(result['hits']['total'], 1)

class QuerySearchTestCase(ElasticSearchTestCase):
    def setUp(self):
        super(QuerySearchTestCase, self).setUp()
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
        self.conn.create_index("test-index")
        self.conn.put_mapping("test-type", {'properties':mapping}, ["test-index"])
        self.conn.index({"name":"Joe Tester", "parsedtext":"Joe Testere nice guy", "uuid":"11111", "position":1}, "test-index", "test-type", 1)
        self.conn.index({"name":"Bill Baloney", "parsedtext":"Joe Testere nice guy", "uuid":"22222", "position":2}, "test-index", "test-type", 2)


        self.conn.refresh(["test-index"])

    def test_TermQuery(self):
        q = TermQuery("name", "joe")
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 1)

        q = TermQuery("name", "joe", 3)
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 1)
        
        q = TermQuery("name", "joe", "3")
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 1)

    def test_WildcardQuery(self):
        q = WildcardQuery("name", "jo*")
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 1)

        q = WildcardQuery("name", "jo*", 3)
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 1)
        
        q = WildcardQuery("name", "jo*", "3")
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 1)

    def test_PrefixQuery(self):
        q = PrefixQuery("name", "jo")
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 1)

        q = PrefixQuery("name", "jo", 3)
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 1)
        
        q = PrefixQuery("name", "jo", "3")
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 1)
        
        
    def test_MatchAllQuery(self):
        q = MatchAllQuery()
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 2)

    def test_StringQuery(self):
        q = StringQuery("joe AND test")
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 0)

        q = StringQuery("joe OR test")
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 2)

        q1 = StringQuery("joe")
        q2 = StringQuery("test")
        q = BoolQuery(must=[q1, q2])
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 0)

        q = BoolQuery(should=[q1, q2])
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 2)

    def test_OR_AND_Filters(self):
        q1= TermQuery("position", 1)
        q2= TermQuery("position", 2)
        andq = ANDFilterQuery([q1, q2])
        
        q = FilteredQuery(MatchAllQuery(), andq)
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 0)

        orq = ORFilterQuery([q1, q2])
        q = FilteredQuery(MatchAllQuery(), orq)
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 2)
        
    def test_FieldQuery(self):
        q = FieldQuery(FieldParameter("name", "+joe"))
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 1)

    def test_DisMaxQuery(self):
        q =  DisMaxQuery(FieldQuery(FieldParameter("name", "+joe")))
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 1)
        
    def test_RegexTermQuery(self):
        q = RegexTermQuery("name", "jo.")
        result = self.conn.search(query = q)
#        pprint(q.q)
#        pprint(result)
        self.assertEquals(result['hits']['total'], 1)

    def test_QueryHighlight(self):
        q = StringQuery("nice")
        q.add_highlight("parsedtext")
        result = self.conn.search(query = q)
        self.assertEquals(result['hits']['total'], 2)

if __name__ == "__main__":
    unittest.main()