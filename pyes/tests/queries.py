#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin and the lang-javascript plugin running on the default port (localhost:9500).
"""
from pyestest import *
from pyes import *

class QuerySearchTestCase(ESTestCase):
    def test_TermQuery(self):
        q = TermQuery("name", "joe")
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 1)

        q = TermQuery("name", "joe", 3)
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 1)
        
        q = TermQuery("name", "joe", "3")
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 1)

    def test_WildcardQuery(self):
        q = WildcardQuery("name", "jo*")
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 1)

        q = WildcardQuery("name", "jo*", 3)
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 1)
        
        q = WildcardQuery("name", "jo*", "3")
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 1)

    def test_PrefixQuery(self):
        q = PrefixQuery("name", "jo")
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 1)

        q = PrefixQuery("name", "jo", 3)
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 1)
        
        q = PrefixQuery("name", "jo", "3")
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 1)
        
    def test_MatchAllQuery(self):
        q = MatchAllQuery()
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 2)

    def test_StringQuery(self):
        q = StringQuery("joe AND test")
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 0)

        q = StringQuery("joe OR test")
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 2)

        q1 = StringQuery("joe")
        q2 = StringQuery("test")
        q = BoolQuery(must=[q1, q2])
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 0)

        q = BoolQuery(should=[q1, q2])
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 2)

    def test_OR_AND_Filters(self):
        q1= TermFilter("position", 1)
        q2= TermFilter("position", 2)
        andq = ANDFilter([q1, q2])
        
        q = FilteredQuery(MatchAllQuery(), andq)
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 0)

        orq = ORFilter([q1, q2])
        q = FilteredQuery(MatchAllQuery(), orq)
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 2)
        
    def test_FieldQuery(self):
        q = FieldQuery(FieldParameter("name", "+joe"))
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 1)

    def test_DisMaxQuery(self):
        q =  DisMaxQuery(FieldQuery(FieldParameter("name", "+joe")))
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 1)
        
    def test_RegexTermQuery(self):
        # Don't run this test, because it depends on the RegexTermQuery
        # feature which is not currently in elasticsearch trunk.
        return

        q = RegexTermQuery("name", "jo.")
        result = self.conn.search(query = q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 1)

    def test_CustomScoreQueryMvel(self):
        q = CustomScoreQuery(query=MatchAllQuery(),
                             lang="mvel",
                             script="_score*(5+doc.position.value)"
                             )
        result = self.conn.search(query=q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 2)
        self.assertEquals(result['hits']['hits'][0]['_score'], 7.0)
        self.assertEquals(result['hits']['hits'][1]['_score'], 6.0)
        self.assertEquals(result['hits']['max_score'], 7.0)

    def test_CustomScoreQueryJS(self):
        q = CustomScoreQuery(query=MatchAllQuery(),
                             lang="js",
                             script="parseFloat(_score*(5+doc.position.value))"
                             )
        result = self.conn.search(query=q, indexes=["test-pindex"])
        self.assertEquals(result['hits']['total'], 2)
        self.assertEquals(result['hits']['hits'][0]['_score'], 7.0)
        self.assertEquals(result['hits']['hits'][1]['_score'], 6.0)
        self.assertEquals(result['hits']['max_score'], 7.0)

if __name__ == "__main__":
    unittest.main()
