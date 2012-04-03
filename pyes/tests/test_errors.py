# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from .estestcase import ESTestCase
from .. import exceptions

class ErrorReportingTestCase(ESTestCase):
    def setUp(self):
        super(ErrorReportingTestCase, self).setUp()
        self.conn.delete_index_if_exists(self.index_name)

    def tearDown(self):
        self.conn.delete_index_if_exists(self.index_name)

    def testCreateDelete(self):
        """Test errors thrown when creating or deleting indices.

        """
        result = self.conn.create_index(self.index_name)
        self.assertTrue('ok' in result)
        self.assertTrue('error' not in result)

        err = self.checkRaises(exceptions.IndexAlreadyExistsException,
            self.conn.create_index, self.index_name)
        self.assertEqual(str(err), "[test-index] Already exists")
        self.assertEqual(err.status, 400)
        self.assertTrue('error' in err.result)
        self.assertTrue('ok' not in err.result)

        result = self.conn.delete_index(self.index_name)
        self.assertTrue('ok' in result)
        self.assertTrue('error' not in result)

        err = self.checkRaises(exceptions.IndexMissingException,
            self.conn.delete_index, self.index_name)
        self.assertEqual(str(err), "[test-index] missing")
        self.assertEqual(err.status, 404)
        self.assertTrue('error' in err.result)
        self.assertTrue('ok' not in err.result)

    def testMissingIndex(self):
        """Test generation of a IndexMissingException.

        """
        err = self.checkRaises(exceptions.IndexMissingException,
            self.conn.flush, self.index_name)
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
