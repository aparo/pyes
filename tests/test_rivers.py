# -*- coding: utf-8 -*-
from __future__ import absolute_import
import unittest
from pyes.tests import ESTestCase
from pyes.rivers import CouchDBRiver, RabbitMQRiver, TwitterRiver

class RiversTestCase(ESTestCase):
    def setUp(self):
        super(RiversTestCase, self).setUp()

    def testCreateCouchDBRiver(self):
        """
        Testing deleting a river
        """
        test_river = CouchDBRiver(index_name='text_index', index_type='test_type')
        result = self.conn.create_river(test_river, river_name='test_index')
        self.assertResultContains(result, {'ok': True})

    def testDeleteCouchDBRiver(self):
        """
        Testing deleting a river
        """
        test_river = CouchDBRiver(index_name='text_index', index_type='test_type')
        result = self.conn.delete_river(test_river, river_name='test_index')
        self.assertResultContains(result, {'ok': True})

    def testCreateRabbitMQRiver(self):
        """
        Testing deleting a river
        """
        test_river = RabbitMQRiver(index_name='text_index', index_type='test_type')
        result = self.conn.create_river(test_river, river_name='test_index')
        self.assertResultContains(result, {'ok': True})

    def testDeleteRabbitMQRiver(self):
        """
        Delete RabbitMQ river
        """
        test_river = RabbitMQRiver(index_name='text_index', index_type='test_type')
        result = self.conn.create_river(test_river, river_name='test_index')
        result = self.conn.delete_river(test_river, river_name='test_index')
        self.assertResultContains(result, {'ok': True})

    def testCreateTwitterRiver(self):
        """
        Create twitter river
        """
        test_river = TwitterRiver('test', 'test', index_name='text_index', index_type='status')
        result = self.conn.create_river(test_river, river_name='test_index')
        self.assertResultContains(result, {'ok': True})

    def testDeleteTwitterRiver(self):
        """
        Delete Twitter river
        """
        test_river = TwitterRiver('test', 'test', index_name='text_index', index_type='status')
        result = self.conn.create_river(test_river, river_name='test_index')
        result = self.conn.delete_river(test_river, river_name='test_index')
        self.assertResultContains(result, {'ok': True})

    def testCreateTwitterRiverOAuth(self):
        test_river = TwitterRiver('test', 'test', index_name='text_index', index_type='test_type',
                                 consumer_key="aaa",
                                 consumer_secret="aaa",
                                 access_token="aaa",
                                 access_token_secret="aaa",
                                 )
        result = self.conn.create_river(test_river, river_name='test_index')
        self.assertResultContains(result, {'ok': True})


if __name__ == "__main__":
    unittest.main()

