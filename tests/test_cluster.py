# -*- coding: utf-8 -*-
from estestcase import ESTestCase

class ClusterTestCase(ESTestCase):
    def setUp(self):
        super(ClusterTestCase, self).setUp()
        mapping = {u'parsedtext': {'boost': 1.0,
                                   'index': 'analyzed',
                                   'store': 'yes',
                                   'type': u'string',
                                   "term_vector": "with_positions_offsets"},
                   u'name': {'boost': 1.0,
                             'index': 'analyzed',
                             'store': 'yes',
                             'type': u'string',
                             "term_vector": "with_positions_offsets"},
                   u'title': {'boost': 1.0,
                              'index': 'analyzed',
                              'store': 'yes',
                              'type': u'string',
                              "term_vector": "with_positions_offsets"},
                   u'pos': {'store': 'yes',
                            'type': u'integer'},
                   u'uuid': {'boost': 1.0,
                             'index': 'not_analyzed',
                             'store': 'yes',
                             'type': u'string'}}
        self.conn.create_index(self.index_name)
        self.conn.put_mapping(self.document_type, {'properties': mapping}, self.index_name)
        self.conn.index({"name": "Joe Tester", "parsedtext": "Joe Testere nice guy", "uuid": "11111", "position": 1},
            self.index_name, self.document_type, 1)
        self.conn.index({"name": "Bill Baloney", "parsedtext": "Bill Testere nice guy", "uuid": "22222", "position": 2},
            self.index_name, self.document_type, 2)
        self.conn.index({"name": "Bill Clinton", "parsedtext": """Bill is not
                nice guy""", "uuid": "33333", "position": 3}, self.index_name, self.document_type, 3)
        self.conn.refresh(self.index_name)

    def test_ClusterState(self):
        result = self.conn.cluster_state()
        self.assertTrue('blocks' in result)
        self.assertTrue('routing_table' in result)

    def test_ClusterNodes(self):
        result = self.conn.cluster_nodes()
        self.assertTrue('cluster_name' in result)
        self.assertTrue('nodes' in result)

    def test_ClusterHealth(self):
        # Make sure that when we get the cluster health, that we get the
        # default keys that we'd expect...
        result = self.conn.cluster_health()
        for key in ['cluster_name', 'status', 'timed_out', 'number_of_nodes',
                    'number_of_data_nodes', 'active_primary_shards',
                    'active_shards', 'relocating_shards', 'initializing_shards',
                    'unassigned_shards']:
            self.assertIn(key, result)

        # We should also make sure that at least /some/ of the keys are
        # the values that we'd expect
        self.assertEqual(result['cluster_name'], 'elasticsearch')
        # Make sure we see the number of active shards we expect
        #self.assertEqual(result['active_shards'], 24)

        # Now let's test that the indices bit actually works
        result = self.conn.cluster_health(indices=['non-existent-index'],
                                          timeout=0, wait_for_status='green')
        # There shouldn't be any active shards on this index
        self.assertEqual(result['active_shards'], 0)
