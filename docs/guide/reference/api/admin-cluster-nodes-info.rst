.. _es-guide-reference-api-admin-cluster-nodes-info:

========================
Admin Cluster Nodes Info
========================

The cluster nodes info API allows to retrieve one or more (or all) of the cluster nodes information.


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/_cluster/nodes'
    
    $ curl -XGET 'http://localhost:9200/_cluster/nodes/nodeId1,nodeId2'


The first command retrieves information of all the nodes in the cluster. The second commands selectively retrieves nodes information of only **nodeId1** and **nodeId2**.

