# -*- coding: utf-8 -*-
#
# Author: Ian Eure <ian@simplegeo.com>
#

import unittest

import pyes.exceptions as exc
import pyes.scriptfields as sf

class ScriptFieldsTest(unittest.TestCase):

    def test_scriptfieldserror_imported(self):
        self.assertTrue(hasattr(sf, 'ScriptFieldsError'))


if __name__ == '__main__':
    unittest.main()
