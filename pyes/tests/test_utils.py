#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'

import unittest
from pyes.tests import ESTestCase
from pyes import clean_string
from pyes.es import ES
from datetime import datetime

"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""

class UtilsTestCase(ESTestCase):

    def test_cleanstring(self):
        self.assertEquals(clean_string("senthil("), "senthil")
        self.assertEquals(clean_string("senthil&"), "senthil")
        self.assertEquals(clean_string("senthil-"), "senthil")
        self.assertEquals(clean_string("senthil:"), "senthil")

    def test_servers(self):
        es = ES("127.0.0.1:9200")
        self.assertEquals(es.servers, [("http", "127.0.0.1", 9200)])
        es = ES("127.0.0.1:9500")
        self.assertEquals(es.servers, [("thrift", "127.0.0.1", 9500)])
        es = ES("http://127.0.0.1:9400")
        self.assertEquals(es.servers, [("http", "127.0.0.1", 9400)])
        es = ES("thrift://127.0.0.1:9100")
        self.assertEquals(es.servers, [("thrift", "127.0.0.1", 9100)])
        es = ES(["thrift://127.0.0.1:9100", "127.0.0.1:9200", ("thrift", "127.0.0.1", 9000)])
        self.assertEquals(sorted(es.servers), [("http", "127.0.0.1", 9200),
                                               ("thrift", "127.0.0.1", 9000),
                                               ("thrift", "127.0.0.1", 9100)])



if __name__ == "__main__":
    unittest.main()
