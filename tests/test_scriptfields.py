# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from pyes import scriptfields

class ScriptFieldsTest(unittest.TestCase):
    def test_scriptfieldserror_imported(self):
        self.assertTrue(hasattr(scriptfields, 'ScriptFieldsError'))

    def test_ignore_failure(self):
        fields = scriptfields.ScriptFields("a_field", "return _source.field", ignore_failure=True)
        serialized = fields.serialize()
        self.assertIn("ignore_failure", serialized.get("a_field", {}))


if __name__ == '__main__':
    unittest.main()
