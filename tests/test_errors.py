# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from pyes.tests import ESTestCase
from pyes import exceptions

class ErrorReportingTestCase(ESTestCase):
    def setUp(self):
        super(ErrorReportingTestCase, self).setUp()
        self.conn.indices.delete_index_if_exists(self.index_name)

    def tearDown(self):
        self.conn.indices.delete_index_if_exists(self.index_name)

    def testCreateDelete(self):
        """Test errors thrown when creating or deleting indices.

        """
        result = self.conn.indices.create_index(self.index_name)
        self.assertTrue('acknowledge' in result)
        self.assertTrue('error' not in result)

        err = self.checkRaises(exceptions.IndexAlreadyExistsException,
            self.conn.indices.create_index, self.index_name)
        self.assertEqual(str(err), "[test-index] already exists")
        self.assertEqual(err.status, 400)
        self.assertTrue('error' in err.result)
        self.assertTrue('ok' not in err.result)

        result = self.conn.indices.delete_index(self.index_name)
        self.assertTrue('ok' in result)
        self.assertTrue('error' not in result)

        err = self.checkRaises(exceptions.IndexMissingException,
            self.conn.indices.delete_index, self.index_name)
        self.assertEqual(str(err), "[test-index] missing")
        self.assertEqual(err.status, 404)
        self.assertTrue('error' in err.result)
        self.assertTrue('ok' not in err.result)

    def testMissingIndex(self):
        """Test generation of a IndexMissingException.

        """
        err = self.checkRaises(exceptions.IndexMissingException,
            self.conn.indices.flush, self.index_name)
        self.assertEqual(str(err), "[test-index] missing")
        self.assertEqual(err.status, 404)
        self.assertTrue('error' in err.result)
        self.assertTrue('ok' not in err.result)

    def testBadRequest(self):
        """Test error reported by doing a bad request.

        """
        err = self.checkRaises(exceptions.ElasticSearchException,
            self.conn._send_request, 'GET', '_bad_request')
        self.assertEqual(str(err), "No handler found for uri [/_bad_request] and method [GET]")
        self.assertEqual(err.status, 400)
        self.assertEqual(err.result, 'No handler found for uri [/_bad_request] and method [GET]')

    def testDelete(self):
        """Test error reported by deleting a missing document.

        """
        self.checkRaises(exceptions.NotFoundException,
            self.conn.delete, self.index_name, "flibble",
            "asdf")


if __name__ == "__main__":
    unittest.main()
