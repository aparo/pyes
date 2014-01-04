# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from pyes.tests import ESTestCase
from pyes.utils import clean_string, make_id
from pyes.es import ES

class UtilsTestCase(ESTestCase):
    def test_cleanstring(self):
        self.assertEqual(clean_string("senthil("), "senthil")
        self.assertEqual(clean_string("senthil&"), "senthil")
        self.assertEqual(clean_string("senthil-"), "senthil")
        self.assertEqual(clean_string("senthil:"), "senthil")

    def test_servers(self):
        geturls = lambda servers: [server.geturl() for server in servers]
        es = ES("127.0.0.1:9200")
        self.assertEqual(geturls(es.servers), ["http://127.0.0.1:9200"])
        es = ES("127.0.0.1:9500")
        self.assertEqual(geturls(es.servers), ["thrift://127.0.0.1:9500"])
        es = ES(("http", "127.0.0.1", 9400))
        self.assertEqual(geturls(es.servers), ["http://127.0.0.1:9400"])
        es = ES(("thrift", "127.0.0.1", 9100))
        self.assertEqual(geturls(es.servers), ["thrift://127.0.0.1:9100"])
        es = ES(["http://127.0.0.1:9100",
                 "127.0.0.1:9200",
                 ("thrift", "127.0.0.1", 9000),
                 "127.0.0.1:9500",
                 ])
        self.assertEqual(geturls(sorted(es.servers)),
                          ["http://127.0.0.1:9100",
                           "http://127.0.0.1:9200",
                           "thrift://127.0.0.1:9000",
                           "thrift://127.0.0.1:9500"])

    def test_make_id(self):
        self.assertEqual(make_id("prova"), "GJu7sAxfT7e7qa2ShfGT0Q")

if __name__ == "__main__":
    unittest.main()
