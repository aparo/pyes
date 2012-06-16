# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from .estestcase import ESTestCase
from ..utils import clean_string
from ..es import ES

class UtilsTestCase(ESTestCase):
    def test_cleanstring(self):
        self.assertEquals(clean_string("senthil("), "senthil")
        self.assertEquals(clean_string("senthil&"), "senthil")
        self.assertEquals(clean_string("senthil-"), "senthil")
        self.assertEquals(clean_string("senthil:"), "senthil")

    def test_servers(self):
        geturls = lambda servers: [server.geturl() for server in servers]
        es = ES("127.0.0.1:9200")
        self.assertEquals(geturls(es.servers), ["http://127.0.0.1:9200"])
        es = ES("127.0.0.1:9500")
        self.assertEquals(geturls(es.servers), ["thrift://127.0.0.1:9500"])
        es = ES(("http", "127.0.0.1", 9400))
        self.assertEquals(geturls(es.servers), ["http://127.0.0.1:9400"])
        es = ES(("thrift", "127.0.0.1", 9100))
        self.assertEquals(geturls(es.servers), ["thrift://127.0.0.1:9100"])
        es = ES(["http://127.0.0.1:9100", 
                 "127.0.0.1:9200", 
                 ("thrift", "127.0.0.1", 9000),
                 "127.0.0.1:9500",
                 ])
        self.assertEquals(geturls(sorted(es.servers)), 
                          ["http://127.0.0.1:9100",
                           "http://127.0.0.1:9200",
                           "thrift://127.0.0.1:9000",
                           "thrift://127.0.0.1:9500"])


if __name__ == "__main__":
    unittest.main()
