#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""
import unittest
from pyes.tests import ESTestCase, get_conn
import StringIO

class DumpCurlTestCase(ESTestCase):
    def setUp(self):
        super(DumpCurlTestCase, self).setUp()

    def testDumpCurl(self):
        """Test errors thrown when creating or deleting indices.

        """
        dump = StringIO.StringIO()
        conn = get_conn(dump_curl=dump)
        result = conn.index(dict(title="Hi"), self.index_name, self.document_type)
        self.assertTrue('ok' in result)
        self.assertTrue('error' not in result)
        dump = dump.getvalue()
        self.assertTrue("""
            curl -XPOST 'http://127.0.0.1:9200/test-index/test-type?pretty=true' -d '{"title": "Hi"}'
            """.strip() in dump)

if __name__ == "__main__":
    unittest.main()
