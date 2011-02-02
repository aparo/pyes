#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin and the lang-javascript plugin running on the default port (localhost:9500).
"""
from pyestest import *
from pyes import *

def setUp():
    """Module level setup.

    These tests don't modify the index, so we just build an index called
    test-mindex once, and use it for all tests.

    """
    mapping = {
        u'parsedtext': {
            'boost': 1.0,
            'index': 'analyzed',
            'store': 'yes',
            'type': u'string',
            "term_vector" : "with_positions_offsets"},
        u'name': {
            'boost': 1.0,
            'index': 'analyzed',
            'store': 'yes',
            'type': u'string',
            "term_vector" : "with_positions_offsets"},
        u'title': {
            'boost': 1.0,
            'index': 'analyzed',
            'store': 'yes',
            'type': u'string',
            "term_vector" : "with_positions_offsets"},
        u'pos': {
            'store': 'yes',
            'type': u'integer'},
        u'uuid': {
            'boost': 1.0,
            'index': 'not_analyzed',
            'store': 'yes',
            'type': u'string'}}
        
    conn = get_conn()
    conn.delete_index_if_exists("test-mindex")
    conn.create_index("test-mindex")
    conn.put_mapping("test-type", {'properties':mapping}, ["test-mindex"])
    conn.index({"name":"Joe Tester", "parsedtext":"Joe Testere nice guy", "uuid":"11111", "position":1}, "test-mindex", "test-type", 1)
    conn.index({"name":"Bill Baloney", "parsedtext":"Joe Testere nice guy", "uuid":"22222", "position":2}, "test-mindex", "test-type", 2)
    conn.refresh(["test-mindex"])

def tearDown():
    """Remove the module level index.

    """
    conn = get_conn()
    conn.delete_index_if_exists("test-mindex")

class QuerySearchTestCase(ESTestCase):
    def test_TermQuery(self):
        q = TermQuery("name", "joe")
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 1)

        q = TermQuery("name", "joe", 3)
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 1)
        
        q = TermQuery("name", "joe", "3")
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 1)

    def test_WildcardQuery(self):
        q = WildcardQuery("name", "jo*")
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 1)

        q = WildcardQuery("name", "jo*", 3)
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 1)
        
        q = WildcardQuery("name", "jo*", "3")
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 1)

    def test_PrefixQuery(self):
        q = PrefixQuery("name", "jo")
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 1)

        q = PrefixQuery("name", "jo", 3)
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 1)
        
        q = PrefixQuery("name", "jo", "3")
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 1)
        
    def test_MatchAllQuery(self):
        q = MatchAllQuery()
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 2)

    def test_StringQuery(self):
        q = StringQuery("joe AND test")
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 0)

        q = StringQuery("joe OR test")
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 2)

        q1 = StringQuery("joe")
        q2 = StringQuery("test")
        q = BoolQuery(must=[q1, q2])
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 0)

        q = BoolQuery(should=[q1, q2])
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 2)

    def test_OR_AND_Filters(self):
        q1= TermFilter("position", 1)
        q2= TermFilter("position", 2)
        andq = ANDFilter([q1, q2])
        
        q = FilteredQuery(MatchAllQuery(), andq)
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 0)

        orq = ORFilter([q1, q2])
        q = FilteredQuery(MatchAllQuery(), orq)
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 2)
        
    def test_FieldQuery(self):
        q = FieldQuery(FieldParameter("name", "+joe"))
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 1)

    def test_DisMaxQuery(self):
        q =  DisMaxQuery(FieldQuery(FieldParameter("name", "+joe")))
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 1)
        
    def test_RegexTermQuery(self):
        # Don't run this test, because it depends on the RegexTermQuery
        # feature which is not currently in elasticsearch trunk.
        return

        q = RegexTermQuery("name", "jo.")
        result = self.conn.search(query = q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 1)

    def test_CustomScoreQueryMvel(self):
        q = CustomScoreQuery(query=MatchAllQuery(),
                             lang="mvel",
                             script="_score*(5+doc.position.value)"
                             )
        result = self.conn.search(query=q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 2)
        self.assertEquals(result['hits']['hits'][0]['_score'], 7.0)
        self.assertEquals(result['hits']['hits'][1]['_score'], 6.0)
        self.assertEquals(result['hits']['max_score'], 7.0)

    def test_CustomScoreQueryJS(self):
        q = CustomScoreQuery(query=MatchAllQuery(),
                             lang="js",
                             script="parseFloat(_score*(5+doc.position.value))"
                             )
        result = self.conn.search(query=q, indexes=["test-mindex"])
        self.assertEquals(result['hits']['total'], 2)
        self.assertEquals(result['hits']['hits'][0]['_score'], 7.0)
        self.assertEquals(result['hits']['hits'][1]['_score'], 6.0)
        self.assertEquals(result['hits']['max_score'], 7.0)

if __name__ == "__main__":
    unittest.main()
