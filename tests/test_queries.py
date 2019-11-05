# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from pyes.tests import ESTestCase
from pyes.es import json
from pyes.query import *
from pyes.filters import TermFilter, ANDFilter, ORFilter, RangeFilter, RawFilter, IdsFilter, MatchAllFilter, NotFilter
from pyes.utils import ESRangeOp

class QuerySearchTestCase(ESTestCase):
    def setUp(self):
        super(QuerySearchTestCase, self).setUp()

        self.conn.indices.create_index(self.index_name)
        self.conn.indices.put_mapping(self.document_type, {'properties': self.get_default_mapping()}, self.index_name)
        self.conn.indices.put_mapping("test-type2", {"_parent": {"type": self.document_type}}, self.index_name)
        self.conn.index({"name": "Joe Tester", "parsedtext": "Joe Testere nice guy", "uuid": "11111", "position": 1, "boost": 1.0},
            self.index_name, self.document_type, 1)
        self.conn.index({"name": "data1", "value": "value1"}, self.index_name, "test-type2", 1, parent=1)
        self.conn.index({"name": "Bill Baloney", "parsedtext": "Bill Testere nice guy", "uuid": "22222", "position": 2, "boost": 2.0},
            self.index_name, self.document_type, 2)
        self.conn.index({"name": "data2", "value": "value2"}, self.index_name, "test-type2", 2, parent=2)
        self.conn.index({"name": "Bill Clinton", "parsedtext": """Bill is not
                nice guy""", "uuid": "33333", "position": 3, "boost": 3.0}, self.index_name, self.document_type, 3)

        self.conn.default_indices = self.index_name

        self.conn.indices.refresh()

    def test_RescoreQuery(self):
        q = FunctionScoreQuery(functions=[FunctionScoreQuery.ScriptScoreFunction(
            lang="mvel",
            script="doc.position.value"
        )])

        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=self.document_type)
        original_results = [x for x in resultset]

        rescore_search = Search(query=q, rescore=RescoreQuery(q, query_weight=1, rescore_query_weight=-10).search(window_size=3))
        rescore_resultset = self.conn.search(query=rescore_search, indices=self.index_name, doc_types=self.document_type)
        rescore_results = [x for x in rescore_resultset]

        rescore_results.reverse()
        self.assertEqual(rescore_search.serialize()['rescore']['window_size'], 3)
        self.assertEqual(original_results, rescore_results)

    def test_TermQuery(self):
        q = TermQuery("name", "joe")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)
        self.assertEqual(q, TermQuery("name", "joe"))
        self.assertNotEquals(q, TermQuery("name", "job"))

        q = TermQuery("name", "joe", 3)
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)
        self.assertEqual(q, TermQuery("name", "joe", 3))
        self.assertNotEquals(q, TermQuery("name", "joe", 4))

        q = TermQuery("name", "joe", "3")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)
        self.assertEqual(q, TermQuery("name", "joe", "3"))
        self.assertNotEquals(q, TermQuery("name", "joe", "4"))

    def test_WildcardQuery(self):
        q = WildcardQuery("name", "jo*")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)
        self.assertEqual(q, WildcardQuery("name", "jo*"))
        self.assertNotEquals(q, WildcardQuery("name", "bo*"))

        q = WildcardQuery("name", "jo*", 3)
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)
        self.assertEqual(q, WildcardQuery("name", "jo*", 3))
        self.assertNotEquals(q, WildcardQuery("name", "jo*", 4))

        q = WildcardQuery("name", "jo*", "3")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)
        self.assertEqual(q, WildcardQuery("name", "jo*", "3"))
        self.assertNotEquals(q, WildcardQuery("name", "jo*", "4"))

    def test_PrefixQuery(self):
        q = PrefixQuery("name", "jo")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)
        self.assertEqual(q, PrefixQuery("name", "jo"))
        self.assertNotEquals(q, PrefixQuery("name", "bo"))

        q = PrefixQuery("name", "jo", 3)
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)
        self.assertEqual(q, PrefixQuery("name", "jo", 3))
        self.assertNotEquals(q, PrefixQuery("name", "jo", 4))

        q = PrefixQuery("name", "jo", "3")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)
        self.assertEqual(q, PrefixQuery("name", "jo", "3"))
        self.assertNotEquals(q, PrefixQuery("name", "jo", "4"))

    def test_SpanMultiQuery(self):
        clause1 = SpanMultiQuery(PrefixQuery("parsedtext", "bi"))
        clause2 = SpanMultiQuery(PrefixQuery("parsedtext", "ni"))
        clauses = [clause1, clause2]
        q = SpanNearQuery(clauses, 1)
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 1)
        self.assertEqual(clause1, SpanMultiQuery(PrefixQuery("parsedtext", "bi")))
        self.assertNotEquals(clause1, clause2)

        clause1 = SpanMultiQuery(WildcardQuery("parsedtext", "bi*"))
        clause2 = SpanMultiQuery(WildcardQuery("parsedtext", "ni*"))
        clauses = [clause1, clause2]
        q = SpanNearQuery(clauses, 1)
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 1)
        self.assertEqual(clause1, SpanMultiQuery(WildcardQuery("parsedtext", "bi*")))
        self.assertNotEquals(clause1, clause2)

        clause1 = SpanMultiQuery(PrefixQuery("parsedtext", "bi"))
        clause2 = SpanMultiQuery(WildcardQuery("parsedtext", "ni*"))
        clauses = [clause1, clause2]
        q = SpanNearQuery(clauses, 1)
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 1)
        self.assertEqual(clause1, SpanMultiQuery(PrefixQuery("parsedtext", "bi")))
        self.assertNotEquals(clause1, clause2)

    def test_MatchAllQuery(self):
        q = MatchAllQuery()
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)
        self.assertEqual(q, MatchAllQuery())

    def test_StringQuery(self):
        q = QueryStringQuery("joe AND test")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 0)
        self.assertEqual(q, QueryStringQuery("joe AND test"))
        self.assertNotEquals(q, QueryStringQuery("moe AND test"))

        q = QueryStringQuery("joe OR test")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)
        self.assertEqual(q, QueryStringQuery("joe OR test"))
        self.assertNotEquals(q, QueryStringQuery("moe OR test"))

        q1 = QueryStringQuery("joe")
        q2 = QueryStringQuery("test")
        q = BoolQuery(must=[q1, q2])
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 0)
        self.assertEqual(q, BoolQuery(must=[QueryStringQuery("joe"), QueryStringQuery("test")]))
        self.assertNotEquals(q, BoolQuery(must=[QueryStringQuery("moe"), QueryStringQuery("test")]))

        q = BoolQuery(should=[q1, q2])
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)
        self.assertEqual(q, BoolQuery(should=[QueryStringQuery("joe"), QueryStringQuery("test")]))
        self.assertNotEquals(q, BoolQuery(should=[QueryStringQuery("moe"), QueryStringQuery("test")]))

        q = QueryStringQuery("joe OR Testere OR guy OR pizza", minimum_should_match="100%")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 0)

        q = QueryStringQuery("joe OR Testere OR guy OR pizza", minimum_should_match="80%")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)

        q = QueryStringQuery("joe OR Testere OR guy OR pizza", minimum_should_match="50%")
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 2)

    def test_OR_AND_Filters(self):
        q1 = TermFilter("position", 1)
        q2 = TermFilter("position", 2)
        andq = ANDFilter([q1, q2])

        q = FilteredQuery(MatchAllQuery(), andq)
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 0)
        self.assertEqual(q, FilteredQuery(MatchAllQuery(),
            ANDFilter([TermFilter("position", 1), TermFilter("position", 2)])))
        self.assertNotEquals(q, FilteredQuery(MatchAllQuery(),
            ANDFilter([TermFilter("position", 1), TermFilter("position", 3)])))

        orq = ORFilter([q1, q2])
        q = FilteredQuery(MatchAllQuery(), orq)
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 2)
        self.assertEqual(q, FilteredQuery(MatchAllQuery(),
            ORFilter([TermFilter("position", 1), TermFilter("position", 2)])))
        self.assertNotEquals(q, FilteredQuery(MatchAllQuery(),
            ORFilter([TermFilter("position", 1), TermFilter("position", 3)])))


    def test_DisMaxQuery(self):
        q = DisMaxQuery(QueryStringQuery(default_field="name", query="+joe"))
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)
        self.assertEqual(q, DisMaxQuery(QueryStringQuery(default_field="name", query="+joe")))
        self.assertNotEquals(q, DisMaxQuery(QueryStringQuery(default_field="name", query="+job")))

    def test_FuzzyQuery(self):
        q = FuzzyQuery('name', 'data')
        resultset = self.conn.search(query=q, indices=self.index_name)

        self.assertEqual(resultset.total, 2)
        self.assertEqual(q, FuzzyQuery('name', 'data'))
        self.assertNotEquals(q, FuzzyQuery('name', 'data2'))

    def test_HasChildQuery(self):
        q = HasChildQuery(type="test-type2", query=TermQuery("name", "data1"))
        resultset = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset.total, 1)
        self.assertEqual(q, HasChildQuery(type="test-type2", query=TermQuery("name", "data1")))
        self.assertNotEquals(q, HasChildQuery(type="test-type2", query=TermQuery("name", "data2")))

    def test_RegexTermQuery(self):
        # Don't run this test, because it depends on the RegexTermQuery
        # feature which is not currently in elasticsearch trunk.
        return

    #        q = RegexTermQuery("name", "jo.")
    #        resultset = self.conn.search(query=q, indices=self.index_name)
    #        self.assertEqual(resultset.total, 1)
    #        # When this test is re-enabled, be sure to add equality and inequality tests (issue 128)

    def test_CustomScoreQueryMvel(self):
        q = FunctionScoreQuery(functions=[FunctionScoreQuery.ScriptScoreFunction(
            lang="mvel",
            script="_score*(5+doc.position.value)"
        )])
        self.assertEqual(q,
            FunctionScoreQuery(functions=[FunctionScoreQuery.ScriptScoreFunction(
                lang="mvel",
                script="_score*(5+doc.position.value)"
            )]))
        self.assertNotEqual(q,
            FunctionScoreQuery(functions=[FunctionScoreQuery.ScriptScoreFunction(
                lang="mvel",
                script="_score*(6+doc.position.value)"
            )]))
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)
        self.assertEqual(resultset[0]._meta.score, 8.0)
        self.assertEqual(resultset[1]._meta.score, 7.0)
        self.assertEqual(resultset.max_score, 8.0)

    def test_CustomScoreQueryJS(self):
        q = FunctionScoreQuery(functions=[FunctionScoreQuery.ScriptScoreFunction(
            lang="js",
            script="parseFloat(_score*(5+doc.position.value))"
        )])
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)
        self.assertEqual(resultset[0]._meta.score, 8.0)
        self.assertEqual(resultset[1]._meta.score, 7.0)
        self.assertEqual(resultset.max_score, 8.0)

    def test_CustomScoreQueryPython(self):
        q = FunctionScoreQuery(functions=[FunctionScoreQuery.ScriptScoreFunction(
            lang="python",
            script="_score*(5+doc['position'].value)"
        )])
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)
        self.assertEqual(resultset[0]._meta.score, 8.0)
        self.assertEqual(resultset[1]._meta.score, 7.0)
        self.assertEqual(resultset.max_score, 8.0)

    def test_Search_stats(self):
        no_stats_group = Search(TermQuery("foo", "bar"))
        one_stats_group = Search(TermQuery("foo", "bar"), stats="hello")
        many_stats_groups = Search(TermQuery("foo", "bar"), stats=["hello", "there", "test"])

        self.assertEqual(no_stats_group.stats, None)
        self.assertEqual(one_stats_group.stats, "hello")
        self.assertEqual(many_stats_groups.stats, ["hello", "there", "test"])

        self.assertEqual(no_stats_group.serialize(),
                {"query": {"term": {"foo": "bar"}}})
        self.assertEqual(one_stats_group.serialize(),
                {"query": {"term": {"foo": "bar"}}, "stats": "hello"})
        self.assertEqual(many_stats_groups.serialize(),
                {"query": {"term": {"foo": "bar"}}, "stats": ["hello", "there", "test"]})

    def test_Search_equality(self):
        self.assertEqual(Search(),
            Search())
        self.assertNotEquals(Search(),
            Search(query=TermQuery("h", "ello")))
        self.assertEqual(Search(query=TermQuery("h", "ello")),
            Search(query=TermQuery("h", "ello")))
        self.assertNotEquals(Search(query=TermQuery("h", "ello")),
            Search(query=TermQuery("j", "ello")))
        self.assertEqual(Search(filter=TermFilter("h", "ello")),
            Search(filter=TermFilter("h", "ello")))
        self.assertNotEquals(Search(filter=TermFilter("h", "ello")),
            Search(filter=TermFilter("j", "ello")))
        self.assertEqual(Search(query=TermQuery("h", "ello"), filter=TermFilter("h", "ello")),
            Search(query=TermQuery("h", "ello"), filter=TermFilter("h", "ello")))
        self.assertNotEquals(Search(query=TermQuery("h", "ello"), filter=TermFilter("h", "ello")),
            Search(query=TermQuery("j", "ello"), filter=TermFilter("j", "ello")))

    def test_ESRange_equality(self):
        self.assertEqual(RangeQuery(),
            RangeQuery())
        self.assertEqual(RangeQuery(ESRange("foo", 1, 2)),
            RangeQuery(ESRange("foo", 1, 2)))
        self.assertNotEquals(RangeQuery(ESRange("foo", 1, 2)),
            RangeQuery(ESRange("bar", 1, 2)))
        self.assertEqual(RangeFilter(),
            RangeFilter())
        self.assertEqual(RangeFilter(ESRange("foo", 1, 2)),
            RangeFilter(ESRange("foo", 1, 2)))
        self.assertNotEquals(RangeFilter(ESRange("foo", 1, 2)),
            RangeFilter(ESRange("bar", 1, 2)))
        self.assertEqual(ESRange("foo"),
            ESRange("foo"))
        self.assertNotEquals(ESRange("foo"),
            ESRange("bar"))
        self.assertEqual(ESRange("foo", 1),
            ESRange("foo", 1))
        self.assertNotEquals(ESRange("foo", 1),
            ESRange("foo", 2))
        self.assertEqual(ESRange("foo", 1, 2),
            ESRange("foo", 1, 2))
        self.assertNotEquals(ESRange("foo", 1, 2),
            ESRange("foo", 1, 3))
        self.assertEqual(ESRange("foo", 1, 2, True, False),
            ESRange("foo", 1, 2, True, False))
        self.assertNotEquals(ESRange("foo", 1, 2, True, False),
            ESRange("foo", 1, 2, False, True))
        self.assertEqual(ESRangeOp("foo", "gt", 5),
            ESRangeOp("foo", "gt", 5))
        self.assertEqual(ESRangeOp("bar", "lt", 6),
            ESRangeOp("bar", "lt", 6))
        self.assertEqual(ESRangeOp("bar", "gt", 3, "lt", 6),
            ESRangeOp("bar", "lt", 6, "gt", 3))

    def test_RawFilter_dict(self):
        filter_ = dict(ids=dict(type="my_type", values=["1", "4", "100"]))
        self.assertEqual(RawFilter(filter_), RawFilter(filter_))
        self.assertEqual(RawFilter(filter_).serialize(), filter_)
        self.assertEqual(RawFilter(filter_).serialize(),
            IdsFilter(type="my_type", values=["1", "4", "100"]).serialize())

    def test_RawFilter_string(self):
        filter_ = dict(ids=dict(type="my_type", values=["1", "4", "100"]))
        filter_string = json.dumps(filter_)
        self.assertEqual(RawFilter(filter_string), RawFilter(filter_string))
        self.assertEqual(RawFilter(filter_string), RawFilter(filter_))
        self.assertEqual(RawFilter(filter_string).serialize(), filter_)
        self.assertEqual(RawFilter(filter_string).serialize(),
            IdsFilter(type="my_type", values=["1", "4", "100"]).serialize())

    def test_RawFilter_search(self):
        filter_ = dict(ids=dict(type="my_type", values=["1", "4", "100"]))
        filter_string = json.dumps(filter_)

        self.assertEqual(Search(filter=RawFilter(filter_)).serialize(),
            dict(filter=filter_))
        self.assertEqual(Search(filter=RawFilter(filter_string)).serialize(),
            dict(filter=filter_))

    # def test_CustomFiltersScoreQuery_ScoreMode(self):
    #     self.assertEqual(CustomFiltersScoreQuery.ScoreMode.FIRST, "first")
    #     self.assertEqual(CustomFiltersScoreQuery.ScoreMode.MIN, "min")
    #     self.assertEqual(CustomFiltersScoreQuery.ScoreMode.MAX, "max")
    #     self.assertEqual(CustomFiltersScoreQuery.ScoreMode.TOTAL, "total")
    #     self.assertEqual(CustomFiltersScoreQuery.ScoreMode.AVG, "avg")
    #     self.assertEqual(CustomFiltersScoreQuery.ScoreMode.MULTIPLY, "multiply")
    #
    # def test_CustomFiltersScoreQuery_Filter(self):
    #     with self.assertRaises(ValueError) as cm:
    #         CustomFiltersScoreQuery.Filter(MatchAllFilter())
    #     self.assertEqual(cm.exception.message, "Exactly one of boost and script must be specified")
    #
    #     with self.assertRaises(ValueError) as cm:
    #         CustomFiltersScoreQuery.Filter(MatchAllFilter(), 5.0, "someScript")
    #     self.assertEqual(cm.exception.message, "Exactly one of boost and script must be specified")
    #
    #     filter1 = CustomFiltersScoreQuery.Filter(MatchAllFilter(), 5.0)
    #     self.assertEqual(filter1, CustomFiltersScoreQuery.Filter(MatchAllFilter(), 5.0))
    #     self.assertEqual(filter1.filter_, MatchAllFilter())
    #     self.assertEqual(filter1.boost, 5.0)
    #     self.assertIsNone(filter1.script)
    #     self.assertEqual(filter1.serialize(), {'filter': {'match_all': {}}, 'boost': 5.0})
    #
    #     filter2 = CustomFiltersScoreQuery.Filter(NotFilter(MatchAllFilter()), script="hello")
    #     self.assertEqual(filter2, CustomFiltersScoreQuery.Filter(NotFilter(MatchAllFilter()), script="hello"))
    #     self.assertEqual(filter2.filter_, NotFilter(MatchAllFilter()))
    #     self.assertEqual(filter2.script, "hello")
    #     self.assertIsNone(filter2.boost)
    #     self.assertEqual(filter2.serialize(), {'filter': {'not': {'filter': {'match_all': {}}}}, 'script': 'hello'})

    def test_CustomFiltersScoreQuery(self):
        script1 = "max(1,2)"
        script2 = "min(1,2)"

        filter1 = FunctionScoreQuery.BoostFunction(boost_factor=5.0, filter=MatchAllFilter())

        filter2 = FunctionScoreQuery.ScriptScoreFunction(script=script1, filter=NotFilter(MatchAllFilter()))
        filter3 = FunctionScoreQuery.ScriptScoreFunction(script=script2, filter=NotFilter(MatchAllFilter()))

        q1 = MatchAllQuery()
        q2 = TermQuery("foo", "bar")

        cfsq1 = FunctionScoreQuery(query=q1, functions=[filter1, filter2])
        self.assertEqual(cfsq1, FunctionScoreQuery(query=q1, functions=[filter1, filter2]))
        self.assertEqual(cfsq1.query, q1)
        self.assertEqual(cfsq1.functions, [filter1, filter2])
        self.assertIsNone(cfsq1.score_mode)
        self.assertIsNone(cfsq1.params)
        # self.assertEqual(cfsq1.serialize(),
        #         {'custom_filters_score': {
        #         'query': {'match_all': {}},
        #         'filters': [
        #             filter1.serialize(),
        #             filter2.serialize()
        #         ]}})
        #
        # params1 = {"foo": "bar"}
        # cfsq2 = FunctionScoreQuery(query=q2, functions=[filter1, filter2, filter3],
        #     score_mode=FunctionScoreQuery.ScoreMode.MAX,
        #     params=params1)
        # self.assertEqual(cfsq2,
        #     FunctionScoreQuery(query=q2, functions=[filter1, filter2, filter3],
        #         score_mode=FunctionScoreQuery.ScoreMode.MAX,
        #         params=params1))
        # self.assertEqual(cfsq2.query, q2)
        # self.assertEqual(cfsq2.filters, [filter1, filter2, filter3])
        # self.assertEqual(cfsq2.score_mode, FunctionScoreQuery.ScoreMode.MAX)
        # self.assertEqual(cfsq2.params, params1)
        # self.assertEqual(cfsq2.serialize(),
        #         {'custom_filters_score': {
        #         'query': {'term': {'foo': 'bar'}},
        #         'filters': [
        #             filter1.serialize(),
        #             filter2.serialize(),
        #             filter3.serialize()
        #         ],
        #         'score_mode': 'max',
        #         'lang': 'mvel',
        #         'params': {"foo": "bar"}}})

    def test_Search_fields(self):
        q = MatchAllQuery()
        all_fields = ["name", "parsedtext", "uuid", "position"]
        resultset = self.conn.search(query=Search(q), indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)
        for result in resultset:
            for field in all_fields:
                self.assertTrue(result.get(field))
        resultset = self.conn.search(query=Search(q,fields=[]), indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)
        for result in resultset:
            for field in all_fields:
                self.assertTrue(not result.get(field))
        resultset = self.conn.search(query=Search(q,fields=['name','position']), indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)
        for result in resultset:
            for field in ['parsedtext','uuid']:
                self.assertTrue(not result.get(field))
            for field in ['name','position']:
                self.assertTrue( result.get(field))

    def test_MatchQuery(self):
        q = MatchQuery("_all", "nice")
        serialized = q.serialize()
        self.assertTrue("match" in serialized)
        self.assertTrue("_all" in serialized["match"])
        self.assertTrue(serialized["match"]["_all"]["query"], "nice")

        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 3)

        q = MatchQuery("_all", "Baloney Testere pizza", operator="and")
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 0)

        q = MatchQuery("_all", "Baloney Testere pizza", operator="or", minimum_should_match="70%")
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 1)

        q = MatchQuery("parsedtext", "Bill guy", type="phrase", slop=2)
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 1)

        q = MatchQuery("parsedtext", "guy Bill", type="phrase", slop=2)
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 0)

        q = MatchQuery("name", "Tester")
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEqual(resultset.total, 1)

    # def test_CustomBoostFactorQuery(self):
    #     q = CustomBoostFactorQuery(query=TermQuery("name", "joe"),
    #         boost_factor=1.0)
    #
    #     resultset = self.conn.search(query=q, indices=self.index_name)
    #
    #     self.assertEqual(resultset.total, 1)
    #     score = resultset.hits[0]['_score']
    #
    #     q = CustomBoostFactorQuery(query=TermQuery("name", "joe"),
    #         boost_factor=2.0)
    #     resultset = self.conn.search(query=q, indices=self.index_name)
    #
    #     score_boosted = resultset.hits[0]['_score']
    #     self.assertEqual(score*2, score_boosted)

    def test_FunctionScoreQuery(self):

        functions = [FunctionScoreQuery.BoostFunction(boost_factor=20, filter=TermFilter('uuid', '33333'))]
        q = FunctionScoreQuery(functions=functions, score_mode=FunctionScoreQuery.ScoreModes.AVG)
        resultset = self.conn.search(query=q, indices=self.index_name)

        self.assertEqual(resultset.hits[0]['_score'], 20)

    def test_FunctionScoreQuery_FieldValueFactor(self):
        functions = [FunctionScoreQuery.FieldValueFactor('boost', factor=2.0)]
        q = FunctionScoreQuery(functions, MatchAllQuery(), score_mode=FunctionScoreQuery.ScoreModes.SUM)
        resultset = self.conn.search(query=q)
        self.assertEqual(resultset.hits[0]['_score'], 6.0)

    def test_FunctionScoreQuery_BoostFunction(self):
        function = FunctionScoreQuery.BoostFunction(2)
        serialized = function.serialize()
        self.assertEqual(serialized, {"boost_factor": 2})

    def test_FunctionScoreQuery_DecayFunction(self):
        function = FunctionScoreQuery.DecayFunction("gauss", "timestamp", scale="4w")
        serialized = function.serialize()
        self.assertEqual(serialized, {"gauss": {"timestamp": {"scale": "4w"}}})

    def test_DeleteByQuery(self):
        q = TermQuery("name", "joe")
        result = self.conn.delete_by_query(self.index_name,
            [self.document_type], q)
        self.assertEqual(result['_indices'][self.index_name]
            ['_shards']['failed'], 0)

if __name__ == "__main__":
    unittest.main()
