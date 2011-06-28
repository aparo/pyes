#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# Author: Ian Eure <ian@simplegeo.com>
#

"""Tests for convert_errors."""

import unittest

from pyes.tests import ESTestCase
from pyes.exceptions import NotFoundException
import pyes.convert_errors as convert_errors


class RaiseIfErrorTestCase(ESTestCase):

    def test_not_found_exception(self):
        self.assertRaises(
            NotFoundException,
            convert_errors.raise_if_error,
            404, {u'_type': u'a_type', u'_id': u'1', u'_index': u'_all'})


if __name__ == '__main__':
    unittest.main()
