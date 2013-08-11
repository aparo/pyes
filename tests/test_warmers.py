# -*- coding: utf-8 -*-
from __future__ import absolute_import
from pyes.tests import ESTestCase
import pyes

class WarmerTestCase(ESTestCase):

    def setUp(self):
        super(WarmerTestCase, self).setUp()
        self.conn.create_index(self.index_name)
        self.conn.refresh(self.index_name)

    def test_put_get_warmer(self):
        warmer1 = pyes.Search(pyes.MatchAllQuery())
        #ES fails if the index is empty
        self.conn.index({'a':1}, self.index_name, self.document_type)
        self.conn.refresh(self.index_name)
        self.conn.put_warmer(indices=[self.index_name], name='w1', warmer=warmer1)
        result = self.conn.get_warmer(indices=[self.index_name], name='w1')
        expected = {
            self.index_name: {
                'warmers': {
                    'w1': {
                        'source': {
                            'query': {'match_all': {}}
                        },
                        'types': []
                    }
                }
            }
        }
        self.assertEqual(result, expected)

    def test_delete_warmer(self):
        warmer1 = pyes.Search(pyes.MatchAllQuery())
        self.conn.put_warmer(indices=[self.index_name], name='w1', warmer=warmer1)
        self.conn.delete_warmer(indices=[self.index_name], name='w1')
        self.assertRaises(
            pyes.exceptions.ElasticSearchException,
            self.conn.get_warmer,
            indices=[self.index_name],
            name='w1'
        )

