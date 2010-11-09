#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""

import unittest
from pyes import ES, file_to_attachment
from pyes.exceptions import NotFoundException
from pprint import pprint
import os

class ESTestCase(unittest.TestCase):
    def setUp(self):
        self.conn = ES('127.0.0.1:9200')
        try:
            self.conn.delete_index("test-index")
        except NotFoundException:
            pass
        
    def tearDown(self):
        try:
            self.conn.delete_index("test-index")
        except NotFoundException:
            pass

    def assertResultContains(self, result, expected):
        for (key, value) in expected.items():
            self.assertEquals(value, result[key])

    def dump(self, result):
        """
        dump to stdout the result
        """
        pprint(result)

main = unittest.main