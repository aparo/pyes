#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin and the lang-javascript plugin running on the default port (localhost:9500).
"""
from pyestest import ESTestCase
from pyes.query import *
from pyes.filters import TermFilter, ANDFilter, ORFilter, RangeFilter
from pyes.utils import ESRangeOp
import unittest

class QuerySearchTestCase(ESTestCase):
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
        self.conn.create_index(self.index_name)
        self.conn.put_mapping(self.document_type, {'properties':mapping}, self.index_name)
        self.conn.put_mapping("test-type2", {"_parent" : {"type" : self.document_type}}, self.index_name)
        self.conn.index({"name":"Joe Tester", "parsedtext":"Joe Testere nice guy", "uuid":"11111", "position":1}, self.index_name, self.document_type, 1)
        self.conn.index({"name":"data1", "value":"value1"}, self.index_name, "test-type2", 1, parent=1)
        self.conn.index({"name":"Bill Baloney", "parsedtext":"Bill Testere nice guy", "uuid":"22222", "position":2}, self.index_name, self.document_type, 2)
        self.conn.index({"name":"data2", "value":"value2"}, self.index_name, "test-type2", 2, parent=2)
        self.conn.index({"name":"Bill Clinton", "parsedtext":"""Bill is not 
                nice guy""", "uuid":"33333", "position":3}, self.index_name, self.document_type, 3)

        self.conn.default_indices = self.index_name

        self.conn.refresh()

    def test_TermQuery(self):
        q = TermQuery("name", "joe")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(q, TermQuery("name", "joe"))
        self.assertNotEquals(q, TermQuery("name", "job"))

        q = TermQuery("name", "joe", 3)
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(q, TermQuery("name", "joe", 3))
        self.assertNotEquals(q, TermQuery("name", "joe", 4))

        q = TermQuery("name", "joe", "3")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(q, TermQuery("name", "joe", "3"))
        self.assertNotEquals(q, TermQuery("name", "joe", "4"))

    def test_WildcardQuery(self):
        q = WildcardQuery("name", "jo*")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(q, WildcardQuery("name", "jo*"))
        self.assertNotEquals(q, WildcardQuery("name", "bo*"))

        q = WildcardQuery("name", "jo*", 3)
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(q, WildcardQuery("name", "jo*", 3))
        self.assertNotEquals(q, WildcardQuery("name", "jo*", 4))

        q = WildcardQuery("name", "jo*", "3")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(q, WildcardQuery("name", "jo*", "3"))
        self.assertNotEquals(q, WildcardQuery("name", "jo*", "4"))

    def test_PrefixQuery(self):
        q = PrefixQuery("name", "jo")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(q, PrefixQuery("name", "jo"))
        self.assertNotEquals(q, PrefixQuery("name", "bo"))

        q = PrefixQuery("name", "jo", 3)
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(q, PrefixQuery("name", "jo", 3))
        self.assertNotEquals(q, PrefixQuery("name", "jo", 4))

        q = PrefixQuery("name", "jo", "3")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(q, PrefixQuery("name", "jo", "3"))
        self.assertNotEquals(q, PrefixQuery("name", "jo", "4"))

    def test_MatchAllQuery(self):
        q = MatchAllQuery()
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEquals(resultset.total, 3)
        self.assertEquals(q, MatchAllQuery())

    def test_StringQuery(self):
        q = StringQuery("joe AND test")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 0)
        self.assertEquals(q, StringQuery("joe AND test"))
        self.assertNotEquals(q, StringQuery("moe AND test"))

        q = StringQuery("joe OR test")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(q, StringQuery("joe OR test"))
        self.assertNotEquals(q, StringQuery("moe OR test"))

        q1 = StringQuery("joe")
        q2 = StringQuery("test")
        q = BoolQuery(must=[q1, q2])
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 0)
        self.assertEquals(q, BoolQuery(must=[StringQuery("joe"), StringQuery("test")]))
        self.assertNotEquals(q, BoolQuery(must=[StringQuery("moe"), StringQuery("test")]))

        q = BoolQuery(should=[q1, q2])
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(q, BoolQuery(should=[StringQuery("joe"), StringQuery("test")]))
        self.assertNotEquals(q, BoolQuery(should=[StringQuery("moe"), StringQuery("test")]))

    def test_OR_AND_Filters(self):
        q1 = TermFilter("position", 1)
        q2 = TermFilter("position", 2)
        andq = ANDFilter([q1, q2])

        q = FilteredQuery(MatchAllQuery(), andq)
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 0)
        self.assertEquals(q, FilteredQuery(MatchAllQuery(),
            ANDFilter([TermFilter("position", 1), TermFilter("position", 2)])))
        self.assertNotEquals(q, FilteredQuery(MatchAllQuery(),
            ANDFilter([TermFilter("position", 1), TermFilter("position", 3)])))

        orq = ORFilter([q1, q2])
        q = FilteredQuery(MatchAllQuery(), orq)
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 2)
        self.assertEquals(q, FilteredQuery(MatchAllQuery(),
            ORFilter([TermFilter("position", 1), TermFilter("position", 2)])))
        self.assertNotEquals(q, FilteredQuery(MatchAllQuery(),
            ORFilter([TermFilter("position", 1), TermFilter("position", 3)])))

    def test_FieldQuery(self):
        q = FieldQuery(FieldParameter("name", "+joe"))
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(q, FieldQuery(FieldParameter("name", "+joe")))
        self.assertNotEquals(q, FieldQuery(FieldParameter("name", "+job")))

    def test_DisMaxQuery(self):
        q = DisMaxQuery(FieldQuery(FieldParameter("name", "+joe")))
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(q, DisMaxQuery(FieldQuery(FieldParameter("name", "+joe"))))
        self.assertNotEquals(q, DisMaxQuery(FieldQuery(FieldParameter("name", "+job"))))

    def test_FuzzyQuery(self):
        q = FuzzyQuery('name', 'data')
        resultset = self.conn.search(query=q, indices=self.index_name)

        self.assertEquals(resultset.total, 2)
        self.assertEquals(q, FuzzyQuery('name', 'data'))
        self.assertNotEquals(q, FuzzyQuery('name', 'data2'))

    def test_HasChildQuery(self):
        q = HasChildQuery(type="test-type2", query=TermQuery("name", "data1"))
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        self.assertEquals(q, HasChildQuery(type="test-type2", query=TermQuery("name", "data1")))
        self.assertNotEquals(q, HasChildQuery(type="test-type2", query=TermQuery("name", "data2")))

    def test_RegexTermQuery(self):
        # Don't run this test, because it depends on the RegexTermQuery
        # feature which is not currently in elasticsearch trunk.
        return

        q = RegexTermQuery("name", "jo.")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEquals(resultset.total, 1)
        # When this test is re-enabled, be sure to add equality and inequality tests (issue 128)

    def test_CustomScoreQueryMvel(self):
        q = CustomScoreQuery(query=MatchAllQuery(),
                             lang="mvel",
                             script="_score*(5+doc.position.value)"
                             )
        self.assertEquals(q,
            CustomScoreQuery(query=MatchAllQuery(),
                             lang="mvel",
                             script="_score*(5+doc.position.value)"
                             ))
        self.assertNotEquals(q,
            CustomScoreQuery(query=MatchAllQuery(),
                             lang="mvel",
                             script="_score*(6+doc.position.value)"
                             ))
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEquals(resultset.total, 3)
        self.assertEquals(resultset[0].meta.score, 8.0)
        self.assertEquals(resultset[1].meta.score, 7.0)
        self.assertEquals(resultset.max_score, 8.0)

    def test_CustomScoreQueryJS(self):
        q = CustomScoreQuery(query=MatchAllQuery(),
                             lang="js",
                             script="parseFloat(_score*(5+doc.position.value))"
                             )
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEquals(resultset.total, 3)
        self.assertEquals(resultset[0].score, 8.0)
        self.assertEquals(resultset[1].score, 7.0)
        self.assertEquals(resultset.max_score, 8.0)

    def test_CustomScoreQueryPython(self):
        q = CustomScoreQuery(query=MatchAllQuery(),
                             lang="python",
                             script="parseFloat(_score*(5+doc.position.value))"
                             )
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEquals(resultset.total, 3)
        self.assertEquals(resultset[0]._score, 8.0)
        self.assertEquals(resultset[1]._score, 7.0)
        self.assertEquals(resultset.max_score, 8.0)

    def test_Search_equality(self):
        self.assertEquals(Search(),
                          Search())
        self.assertNotEquals(Search(),
                             Search(query=TermQuery("h", "ello")))
        self.assertEquals(Search(query=TermQuery("h", "ello")),
                          Search(query=TermQuery("h", "ello")))
        self.assertNotEquals(Search(query=TermQuery("h", "ello")),
                             Search(query=TermQuery("j", "ello")))
        self.assertEquals(Search(filter=TermFilter("h", "ello")),
                          Search(filter=TermFilter("h", "ello")))
        self.assertNotEquals(Search(filter=TermFilter("h", "ello")),
                             Search(filter=TermFilter("j", "ello")))
        self.assertEquals(Search(query=TermQuery("h", "ello"), filter=TermFilter("h", "ello")),
                          Search(query=TermQuery("h", "ello"), filter=TermFilter("h", "ello")))
        self.assertNotEquals(Search(query=TermQuery("h", "ello"), filter=TermFilter("h", "ello")),
                             Search(query=TermQuery("j", "ello"), filter=TermFilter("j", "ello")))
        
    def test_ESRange_equality(self):
        self.assertEquals(RangeQuery(),
          RangeQuery())
        self.assertEquals(RangeQuery(ESRange("foo", 1, 2)),
          RangeQuery(ESRange("foo", 1, 2)))
        self.assertNotEquals(RangeQuery(ESRange("foo", 1, 2)),
          RangeQuery(ESRange("bar", 1, 2)))
        self.assertEquals(RangeFilter(),
          RangeFilter())
        self.assertEquals(RangeFilter(ESRange("foo", 1, 2)),
          RangeFilter(ESRange("foo", 1, 2)))
        self.assertNotEquals(RangeFilter(ESRange("foo", 1, 2)),
          RangeFilter(ESRange("bar", 1, 2)))
        self.assertEquals(ESRange("foo"),
          ESRange("foo"))
        self.assertNotEquals(ESRange("foo"),
          ESRange("bar"))
        self.assertEquals(ESRange("foo", 1),
          ESRange("foo", 1))
        self.assertNotEquals(ESRange("foo", 1),
          ESRange("foo", 2))
        self.assertEquals(ESRange("foo", 1, 2),
          ESRange("foo", 1, 2))
        self.assertNotEquals(ESRange("foo", 1, 2),
          ESRange("foo", 1, 3))
        self.assertEquals(ESRange("foo", 1, 2, True, False),
          ESRange("foo", 1, 2, True, False))
        self.assertNotEquals(ESRange("foo", 1, 2, True, False),
          ESRange("foo", 1,2, False, True))
        self.assertEquals(ESRangeOp("foo", "gt", 5),
          ESRangeOp("foo", "gt", 5))
        self.assertEquals(ESRangeOp("bar", "lt", 6),
          ESRangeOp("bar", "lt", 6))

if __name__ == "__main__":
    unittest.main()
