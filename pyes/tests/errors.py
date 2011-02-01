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
        """Test errors thrown when creating or deleting indexes.

        """
        try:
            self.conn.delete_index("test-index")
        except pyes.exceptions.NotFoundException:
            pass

        self.conn.create_index("test-index")
        err = self.checkRaises(pyes.exceptions.AlreadyExistsException,
                               self.conn.create_index, "test-index")
        self.assertEqual(str(err), "[test-index] Already exists")
        self.assertEqual(err.status, 400)
        self.assertTrue('error' in err.result)
        self.assertTrue('ok' not in err.result)

        self.conn.delete_index("test-index")
        err = self.checkRaises(pyes.exceptions.NotFoundException,
                               self.conn.delete_index, "test-index")
        self.assertEqual(str(err), "[test-index] missing")
        self.assertEqual(err.status, 400)
        self.assertTrue('error' in err.result)
        self.assertTrue('ok' not in err.result)

    def testMissingIndex(self):
        """Test generation of a IndexMissingException.

        """
        try:
            self.conn.delete_index("test-index")
        except pyes.exceptions.NotFoundException:
            pass
        err = self.checkRaises(pyes.exceptions.IndexMissingException,
                               self.conn.flush, 'test-index')
        self.assertEqual(str(err), "[test-index] missing")
        self.assertEqual(err.status, 500)
        self.assertTrue('error' in err.result)
        self.assertTrue('ok' not in err.result)

if __name__ == "__main__":
    unittest.main()
