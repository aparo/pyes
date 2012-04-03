# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from .estestcase import ESTestCase
from ..exceptions import (NotFoundException, IndexAlreadyExistsException)
from .. import convert_errors


class RaiseIfErrorTestCase(ESTestCase):
    def test_not_found_exception(self):
        self.assertRaises(
            NotFoundException,
            convert_errors.raise_if_error,
            404, {u'_type': u'a_type', u'_id': u'1', u'_index': u'_all'})

    def test_nested_index_already_exists_exception(self):
        self.assertRaises(
            IndexAlreadyExistsException,
            convert_errors.raise_if_error,
            400, {u'status': 400,
                  u'error': (u'RemoteTransportException[[name][inet' +
                             u'[/127.0.0.1:9300]][indices/createIndex]]; ' +
                             u'nested: IndexAlreadyExistsException[' +
                             u'[test-index] Already exists]; ')})

if __name__ == '__main__':
    unittest.main()
