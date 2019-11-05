# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from pyes.tests import ESTestCase

class IndexStatsTestCase(ESTestCase):
    def setUp(self):
        super(IndexStatsTestCase, self).setUp()

        self.conn.indices.create_index(self.index_name)
        self.conn.indices.put_mapping(self.document_type, {'properties': self.get_default_mapping()}, self.index_name)
        self.conn.indices.put_mapping("test-type2", {"_parent": {"type": self.document_type}}, self.index_name)
        self.conn.index({"name": "Joe Tester", "parsedtext": "Joe Testere nice guy", "uuid": "11111", "position": 1},
            self.index_name, self.document_type, 1)
        self.conn.index({"name": "data1", "value": "value1"}, self.index_name, "test-type2", 1, parent=1)
        self.conn.index({"name": "Bill Baloney", "parsedtext": "Bill Testere nice guy", "uuid": "22222", "position": 2},
            self.index_name, self.document_type, 2)
        self.conn.index({"name": "data2", "value": "value2"}, self.index_name, "test-type2", 2, parent=2)
        self.conn.index({"name": "Bill Clinton", "parsedtext": """Bill is not
                nice guy""", "uuid": "33333", "position": 3}, self.index_name, self.document_type, 3)

        self.conn.default_indices = self.index_name

        self.conn.indices.refresh()

    def test_all_indices(self):
        result = self.conn.indices.stats()
        self.assertEqual(5, result._all.total.docs.count)

    def test_select_indices(self):
        result = self.conn.indices.stats(self.index_name)
        self.assertEqual(5, result._all.total.docs.count)

    def test_optimize(self):
        result = self.conn.indices.optimize(indices=self.index_name, wait_for_merge=True, max_num_segments=1)
        self.assertEqual(result._shards["failed"], 0)

if __name__ == "__main__":
    unittest.main()
