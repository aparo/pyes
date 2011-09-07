#!/usr/bin/env python
# -*- coding: utf-8 -*-

__author__ = 'Alberto Paro'

import unittest
from pyes.tests import ESTestCase

"""
Unit tests for pyes.  These require an es server with thrift plugin running on the default port (localhost:9500).
"""

class ElasticSearchModelTestCase(ESTestCase):
    def setUp(self):
        super(ElasticSearchModelTestCase, self).setUp()
        self.init_default_index()

    def test_ElasticSearchModel_init(self):
        obj = self.conn.factory_object(self.index_name, self.document_type, {"name":"test", "val":1})
        self.assertEqual(obj.name, "test")
        obj.name = "aaa"
        self.assertEqual(obj.name, "aaa")
        self.assertEqual(obj.val, 1)
        self.assertEqual(obj.meta.id, None)
        obj.meta.id = "dasdas"
        self.assertEqual(obj.meta.id, "dasdas")
        self.assertEqual(sorted(obj.keys()), ["name", "val"])
        obj.save()
        obj.name = "test2"
        obj.save()

        reloaded = self.conn.get(self.index_name, self.document_type, obj.meta.id)
        self.assertEqual(reloaded.name, "test2")


if __name__ == "__main__":
    unittest.main()
