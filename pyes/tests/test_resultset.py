#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'

import unittest
from pyes.tests import ESTestCase
from pyes.query import MatchAllQuery, Search

"""
Unit tests for pyes  These require an es server with thrift plugin running on the default port (localhost:9500).
"""

class ResultsetTestCase(ESTestCase):
    def setUp(self):
        super(ResultsetTestCase, self).setUp()
        self.init_default_index()

        for i in xrange(1000):
                self.conn.index({"name":"Joe Tester%d" % i, "parsedtext":"Joe Testere nice guy", "uuid":"11111", "position":i}, self.index_name, self.document_type, i, bulk=True)
        self.conn.refresh(self.index_name)

    def test_iterator(self):
        resultset = self.conn.search(Search(MatchAllQuery(), size=10), self.index_name, self.document_type)
        self.assertEqual(len([p for p in resultset[:10]]), 10)
        self.assertEqual(resultset[10].uuid, "11111")
        self.assertEqual(resultset.total, 1000)



if __name__ == "__main__":
    unittest.main()
