# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from .estestcase import ESTestCase
from ..facets import DateHistogramFacet
from ..filters import TermFilter, RangeFilter
from ..query import FilteredQuery, MatchAllQuery, Search
from ..utils import ESRange
import datetime

class FacetSearchTestCase(ESTestCase):
    def setUp(self):
        super(FacetSearchTestCase, self).setUp()
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
                   u'position': {'store': 'yes',
                                 'type': u'integer'},
                   u'tag': {'store': 'yes',
                            'type': u'string'},
                   u'date': {'store': 'yes',
                             'type': u'date'},
                   u'uuid': {'boost': 1.0,
                             'index': 'not_analyzed',
                             'store': 'yes',
                             'type': u'string'}}
        self.conn.create_index(self.index_name)
        self.conn.put_mapping(self.document_type, {'properties': mapping}, self.index_name)
        self.conn.index({"name": "Joe Tester",
                         "parsedtext": "Joe Testere nice guy",
                         "uuid": "11111",
                         "position": 1,
                         "tag": "foo",
                         "date": datetime.date(2011, 5, 16)},
            self.index_name, self.document_type, 1)
        self.conn.index({"name": " Bill Baloney",
                         "parsedtext": "Bill Testere nice guy",
                         "uuid": "22222",
                         "position": 2,
                         "tag": "foo",
                         "date": datetime.date(2011, 4, 16)},
            self.index_name, self.document_type, 2)
        self.conn.index({"name": "Bill Clinton",
                         "parsedtext": "Bill is not nice guy",
                         "uuid": "33333",
                         "position": 3,
                         "tag": "bar",
                         "date": datetime.date(2011, 4, 28)},
            self.index_name, self.document_type, 3)
        self.conn.refresh(self.index_name)

    def test_terms_facet(self):
        q = MatchAllQuery()
        q = q.search()
        q.facet.add_term_facet('tag')
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEquals(resultset.total, 3)
        self.assertEquals(resultset.facets.tag.terms, [{u'count': 2, u'term': u'foo'},
                {u'count': 1, u'term': u'bar'}])

        q2 = MatchAllQuery()
        q2 = q2.search()
        q2.facet.add_term_facet('tag')
        q3 = MatchAllQuery()
        q3 = q3.search()
        q3.facet.add_term_facet('tag')
        self.assertEquals(q2, q3)

        q4 = MatchAllQuery()
        q4 = q4.search()
        q4.facet.add_term_facet('bag')
        self.assertNotEquals(q2, q4)

    def test_terms_facet_filter(self):
        q = MatchAllQuery()
        q = FilteredQuery(q, TermFilter('tag', 'foo'))
        q = q.search()
        q.facet.add_term_facet('tag')
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEquals(resultset.total, 2)
        self.assertEquals(resultset.facets['tag']['terms'], [{u'count': 2, u'term': u'foo'}])
        self.assertEquals(resultset.facets.tag.terms, [{u'count': 2, u'term': u'foo'}])

        q2 = MatchAllQuery()
        q2 = FilteredQuery(q2, TermFilter('tag', 'foo'))
        q2 = q2.search()
        q2.facet.add_term_facet('tag')
        q3 = MatchAllQuery()
        q3 = FilteredQuery(q3, TermFilter('tag', 'foo'))
        q3 = q3.search()
        q3.facet.add_term_facet('tag')
        self.assertEquals(q2, q3)

        q4 = MatchAllQuery()
        q4 = FilteredQuery(q4, TermFilter('tag', 'foo'))
        q4 = q4.search()
        q4.facet.add_term_facet('bag')
        self.assertNotEquals(q3, q4)

    def test_date_facet(self):
        q = MatchAllQuery()
        q = q.search()
        q.facet.facets.append(DateHistogramFacet('date_facet',
            field='date',
            interval='month'))
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEquals(resultset.total, 3)
        self.assertEquals(resultset.facets.date_facet.entries, [{u'count': 2, u'time': 1301616000000},
                {u'count': 1, u'time': 1304208000000}])
        self.assertEquals(datetime.datetime.fromtimestamp(1301616000000 / 1000.).date(),
            datetime.date(2011, 04, 01))
        self.assertEquals(datetime.datetime.fromtimestamp(1304208000000 / 1000.).date(),
            datetime.date(2011, 05, 01))

    def test_date_facet_filter(self):
        q = MatchAllQuery()
        q = FilteredQuery(q, RangeFilter(qrange=ESRange('date',
            datetime.date(2011, 4, 1),
            datetime.date(2011, 5, 1),
            include_upper=False)))
        q = q.search()
        q.facet.facets.append(DateHistogramFacet('date_facet',
            field='date',
            interval='month'))
        resultset = self.conn.search(query=q, indices=self.index_name, doc_types=[self.document_type])
        self.assertEquals(resultset.total, 2)
        self.assertEquals(resultset.facets['date_facet']['entries'], [{u'count': 2, u'time': 1301616000000}])

if __name__ == "__main__":
    unittest.main()
