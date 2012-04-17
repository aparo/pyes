# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from .. import scriptfields

class ScriptFieldsTest(unittest.TestCase):
    def test_scriptfieldserror_imported(self):
        self.assertTrue(hasattr(scriptfields, 'ScriptFieldsError'))


if __name__ == '__main__':
    unittest.main()
