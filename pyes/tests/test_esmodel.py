# -*- coding: utf-8 -*-
from __future__ import absolute_import
from copy import deepcopy
import unittest
from .estestcase import ESTestCase
from ..es import DotDict

class ElasticSearchModelTestCase(ESTestCase):
    def setUp(self):
        super(ElasticSearchModelTestCase, self).setUp()
        self.init_default_index()

    def test_ElasticSearchModel_init(self):
        obj = self.conn.factory_object(self.index_name, self.document_type, {"name": "test", "val": 1})
        self.assertEqual(obj.name, "test")
        obj.name = "aaa"
        self.assertEqual(obj.name, "aaa")
        self.assertEqual(obj.val, 1)
        self.assertEqual(obj._meta.id, None)
        obj._meta.id = "dasdas"
        self.assertEqual(obj._meta.id, "dasdas")
        self.assertEqual(sorted(obj.keys()), ["name", "val"])
        obj.save()
        obj.name = "test2"
        obj.save()

        reloaded = self.conn.get(self.index_name, self.document_type, obj._meta.id)
        self.assertEqual(reloaded.name, "test2")

    def test_DotDict(self):
        dotdict = DotDict(foo="bar")
        dotdict2 = deepcopy(dotdict)
        dotdict2["foo"] = "baz"
        self.assertEqual(dotdict["foo"], "bar")
        self.assertEqual(dotdict2["foo"], "baz")
        self.assertEqual(type(dotdict2), DotDict)

        dotdict = DotDict(foo="bar", bar=DotDict(baz="qux"))
        dotdict2 = deepcopy(dotdict)
        dotdict2["bar"]["baz"] = "foo"
        self.assertEqual(dotdict["bar"]["baz"], "qux")
        self.assertEqual(dotdict2["bar"]["baz"], "foo")
        self.assertEqual(type(dotdict2), DotDict)

if __name__ == "__main__":
    unittest.main()
