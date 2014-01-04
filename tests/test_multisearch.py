# -*- coding: utf-8 -*-
from __future__ import absolute_import
import six
import io
import unittest
from pyes.tests import ESTestCase
from pyes.es import json
from pyes.query import *
from pyes.filters import TermFilter, ANDFilter, ORFilter, RangeFilter, RawFilter, IdsFilter, MatchAllFilter, NotFilter
from pyes.utils import ESRangeOp

if six.PY2:
    class UnicodeWriter(io.StringIO):
        def write(self, ss, *args, **kwargs):
            super(UnicodeWriter, self).write(unicode(ss), *args, **kwargs)
else:
    class UnicodeWriter(io.BytesIO):
        def write(self, ss, *args, **kwargs):
            super(UnicodeWriter, self).write(ss, *args, **kwargs)


class MultiSearchTestCase(ESTestCase):
    def setUp(self):
        super(MultiSearchTestCase, self).setUp()
        mapping = {u'name': {'boost': 1.0,
                             'index': 'analyzed',
                             'store': 'yes',
                             'type': u'string',
                             "term_vector": "with_positions_offsets"},
                   u'title': {'boost': 1.0,
                              'index': 'analyzed',
                              'store': 'yes',
                              'type': u'string',
                              "term_vector": "with_positions_offsets"}}
        self.conn.indices.create_index(self.index_name)
        self.conn.indices.put_mapping(self.document_type, {'properties': mapping}, self.index_name)
        self.conn.index({"name": "Joe Tester", "title": "Joe Testere nice guy"},
            self.index_name, self.document_type, 1)
        self.conn.index({"name": "Bill Baloney", "title": "Bill Testere nice guy"},
            self.index_name, self.document_type, 2)
        self.conn.index({"name": "Bill Clinton", "title": """Bill is not
                nice guy"""}, self.index_name, self.document_type, 3)

        #self.conn.default_indices = self.index_name

        self.curl_writer = UnicodeWriter()
        self.conn.dump_curl = self.curl_writer

        self.conn.indices.refresh()

    def _compute_num_requests(self):
        self.curl_writer.flush()
        self.curl_writer.seek(0)

        return len(self.curl_writer.read().decode("utf8").split('\n'))

    def test_TermQuery_simple_multi(self):
        """Compare multi search with simple single query."""
        # make sure single search returns something
        q = TermQuery("name", "joe")
        resultset_single = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset_single.total, 1)

        # now check that multi query returns the same results
        resultset_multi = self.conn.search_multi([q], indices_list=[self.index_name])
        # perform the search
        resultset_multi._do_search()

        self.assertTrue(resultset_multi.valid)
        self.assertEqual(resultset_multi[0].total, 1)
        self.assertDictEqual(resultset_multi[0][0], resultset_single[0])

    def test_TermQuery_double_multi(self):
        """Perform two multi searches."""
        q1 = TermQuery("name", "joe")
        q2 = TermQuery("name", "clinton")

        resultset_single1 = self.conn.search(query=q1, indices=self.index_name)
        resultset_single2 = self.conn.search(query=q2, indices=self.index_name)
        self.assertEqual(resultset_single1.total, 1)
        self.assertEqual(resultset_single2.total, 1)

        # now check that multi query returns the same results
        resultset_multi = self.conn.search_multi([q1, q2],
                                                 indices_list=[self.index_name] * 2)
        resultset_multi._do_search()

        self.assertTrue(resultset_multi.valid)
        self.assertEqual(resultset_multi[0].total, 1)
        self.assertEqual(resultset_multi[1].total, 1)
        self.assertDictEqual(resultset_multi[0][0], resultset_single1[0])
        self.assertDictEqual(resultset_multi[1][0], resultset_single2[0])

    def test_size_multi(self):
        """Make sure that 'size' parameter works correctly."""
        q = TermQuery("name", "bill")
        resultset_single = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset_single.total, 2)

        s = Search(query=q, size=1)
        resultset_multi = self.conn.search_multi([s], indices_list=[self.index_name])
        resultset_multi._do_search()

        num_curl_requests = self._compute_num_requests()

        self.assertTrue(resultset_multi.valid)
        self.assertEqual(len(resultset_multi[0].hits), 1)
        self.assertIn(resultset_multi[0][0], resultset_single)

        # no curl requests should have been triggered when doing
        # resultset_multi[0][0]
        self.assertEqual(num_curl_requests,
                         self._compute_num_requests())

        # make sure that getting more than 'size' elements triggers
        # an ES request
        self.assertIn(resultset_multi[0][1], resultset_single)
        self.assertLess(num_curl_requests-1,
                        self._compute_num_requests())

    def test_start_multi(self):
        """Make sure that 'start' parameter works correctly."""
        q = TermQuery("name", "bill")
        resultset_single = self.conn.search(query=q, indices=self.index_name)
        self.assertEqual(resultset_single.total, 2)

        s = Search(query=q, start=1)
        resultset_multi = self.conn.search_multi([s], indices_list=[self.index_name])
        resultset_multi._do_search()

        self.assertTrue(resultset_multi.valid)
        self.assertEqual(len(resultset_multi[0].hits), 1)
        self.assertIn(resultset_multi[0][0], resultset_single)


if __name__ == "__main__":
    unittest.main()
