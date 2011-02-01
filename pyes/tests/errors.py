#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""
import unittest
from pyes.tests import ESTestCase
import pyes.exceptions

class ErrorReportingTestCase(ESTestCase):
    def setUp(self):
        super(ErrorReportingTestCase, self).setUp()

    def testCreateDelete(self):
        """

        Test errors thrown when creating or deleting.

        """
        try:
            self.conn.delete_index("test-index")
        except pyes.exceptions.NotFoundException:
            pass
        self.conn.create_index("test-index")
        self.assertRaises(pyes.exceptions.AlreadyExistsException, self.conn.create_index, "test-index")
        self.conn.delete_index("test-index")
        self.assertRaises(pyes.exceptions.NotFoundException, self.conn.delete_index, "test-index")

if __name__ == "__main__":
    unittest.main()
