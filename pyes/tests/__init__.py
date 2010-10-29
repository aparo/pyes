#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""

import unittest
from pyes import ES, file_to_attachment
from pprint import pprint
import os

class ESTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = ES('127.0.0.1:9500')
        self.conn.delete_index("test-index")
        
    def tearDown(self):
        self.conn.delete_index("test-index")

    def assertResultContains(self, result, expected):
        for (key, value) in expected.items():
            self.assertEquals(value, result[key])

    def dump(self, result):
        """
        dump to stdout the result
        """
        from pprint import pprint
        pprint(result)

if __name__ == "__main__":
    unittest.main()
#    suite = unittest.TestLoader().loadTestsFromTestCase(GeoQuerySearchTestCase)
#    suite = unittest.TestLoader().loadTestsFromTestCase(IndexingTestCase)
#    suite = unittest.TestLoader().loadTestsFromTestCase(BulkTestCase)
#    suite = unittest.TestLoader().loadTestsFromTestCase(QueryAttachmentTestCase)
#    suite = unittest.TestLoader().loadTestsFromTestCase(QuerySearchTestCase)
#    suite = unittest.TestLoader().loadTestsFromTestCase(SearchTestCase)
#    unittest.TextTestRunner(verbosity=2).run(suite)