# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from .estestcase import ESTestCase


class ScriptFilterTestCase(ESTestCase):

    def test_lang(self):
        from pyes.filters import ScriptFilter
        f = ScriptFilter(
            'name',
            params={
                'param_1': 1,
                'param_2': 'boo',
            },
            lang='native'
        )
        expected = {
            'script': {
                'params': {
                    'param_1': 1,
                    'param_2': 'boo'},
                'script': 'name',
                'lang': 'native',
            }
        }
        self.assertEqual(expected, f.serialize())

if __name__ == "__main__":
    unittest.main()
