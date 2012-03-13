.. _es-guide-reference-api-admin-cluster-nodes-stats:

=========================
Admin Cluster Nodes Stats
=========================

The cluster nodes stats API allows to retrieve one or more (or all) of the cluster nodes statistics.


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/_cluster/nodes/stats'
    
    $ curl -XGET 'http://localhost:9200/_cluster/nodes/nodeId1,nodeId2/stats'


The first command retrieves stats of all the nodes in the cluster. The second commands selectively retrieves nodes stats of only **nodeId1** and **nodeId2**.

