# -*- coding: utf-8 -*-
from pyes.tests import ESTestCase

class UpdateTestCase(ESTestCase):
    def setUp(self):
        super(UpdateTestCase, self).setUp()
        self.conn.indices.create_index(self.index_name)
        self.conn.index({"counter": 0}, self.index_name, self.document_type, 1)

    def testPartialUpdateWithoutParams(self):
        self.conn.partial_update(self.index_name, self.document_type, 1, script="ctx._source.counter = 2")
        doc = self.conn.get(self.index_name, self.document_type, 1)
        self.assertEqual(doc["counter"], 2)

    def testPartialUpdateWithParams(self):
        self.conn.partial_update(self.index_name, self.document_type, 1, script="ctx._source.counter = param1", params={"param1": 3})
        doc = self.conn.get(self.index_name, self.document_type, 1)
        self.assertEqual(doc["counter"], 3)

    def testPartialUpdateWithUpsert(self):
        self.conn.partial_update(self.index_name, self.document_type, 2, script="ctx._source.counter += 1", upsert={"counter": 5})
        doc = self.conn.get(self.index_name, self.document_type, 2)
        self.assertEqual(doc["counter"], 5)

if __name__ == "__main__":
    import unittest
    unittest.main()
