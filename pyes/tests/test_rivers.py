# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from .estestcase import ESTestCase
from ..rivers import CouchDBRiver, RabbitMQRiver, TwitterRiver

class RiversTestCase(ESTestCase):
    def setUp(self):
        super(RiversTestCase, self).setUp()

    def testCreateCouchDBRiver(self):
        """
        Testing deleting a river
        """
        test_river = CouchDBRiver(index_name='text_index', index_type='test_type')
        result = self.conn.create_river(test_river, river_name='test_index')
        print result
        self.assertResultContains(result, {'ok': True})

    def testDeleteCouchDBRiver(self):
        """
        Testing deleting a river
        """
        test_river = CouchDBRiver(index_name='text_index', index_type='test_type')
        result = self.conn.delete_river(test_river, river_name='test_index')
        print result
        self.assertResultContains(result, {'ok': True})

    def testCreateRabbitMQRiver(self):
        """
        Testing deleting a river
        """
        test_river = RabbitMQRiver(index_name='text_index', index_type='test_type')
        result = self.conn.create_river(test_river, river_name='test_index')
        print result
        self.assertResultContains(result, {'ok': True})

    def testDeleteRabbitMQRiver(self):
        """
        Testing deleting a river
        """
        test_river = RabbitMQRiver(index_name='text_index', index_type='test_type')
        result = self.conn.delete_river(test_river, river_name='test_index')
        print result
        self.assertResultContains(result, {'ok': True})

    def testCreateTwitterRiver(self):
        """
        Testing deleting a river
        """
        test_river = TwitterRiver('test', 'test', index_name='text_index', index_type='test_type')
        result = self.conn.create_river(test_river, river_name='test_index')
        print result
        self.assertResultContains(result, {'ok': True})

    def testDeleteTwitterRiver(self):
        """
        Testing deleting a river
        """
        test_river = TwitterRiver('test', 'test', index_name='text_index', index_type='test_type')
        result = self.conn.delete_river(test_river, river_name='test_index')
        print result
        self.assertResultContains(result, {'ok': True})

if __name__ == "__main__":
    unittest.main()

