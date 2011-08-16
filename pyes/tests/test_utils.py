#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'

import unittest
from pyes.tests import ESTestCase
from pyes import TermQuery, clean_string
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

if __name__ == "__main__":
    unittest.main()
