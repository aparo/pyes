.. _es-guide-reference-api-admin-cluster-nodes-stats:

=========================
Admin Cluster Nodes Stats
=========================

The cluster nodes stats API allows to retrieve one or more (or all) of the cluster nodes statistics.


.. code-block:: js

    curl -XGET 'http://localhost:9200/_cluster/nodes/stats'
    curl -XGET 'http://localhost:9200/_cluster/nodes/nodeId1,nodeId2/stats'
    
    # simplified
    curl -XGET 'http://localhost:9200/_nodes/stats'
    curl -XGET 'http://localhost:9200/_nodes/nodeId1,nodeId2/stats'


The first command retrieves stats of all the nodes in the cluster. The second command selectively retrieves nodes stats of only **nodeId1** and **nodeId2**. All the nodes selective options are explained :ref:`here <es-guide-reference-api-index>`.  

By default, **indices** stats are returned. With options for **indices**, **os**, **process**, **jvm**, **network**, **transport**, **http**, **fs**, and **thread_pool**. For example:


.. code-block:: js

    # return indices and os    
    curl -XGET 'http://localhost:9200/_nodes/stats?os=true'
    # return just os and process
    curl -XGET 'http://localhost:9200/_nodes/stats?clear=true&os=true&process=true'
    # specific type endpoint
    curl -XGET 'http://localhost:9200/_nodes/process/stats'
    curl -XGET 'http://localhost:9200/_nodes/10.0.0.1/process/stats'
    # or, if you like the other way
    curl -XGET 'http://localhost:9200/_nodes/stats/process'
    curl -XGET 'http://localhost:9200/_nodes/10.0.01/stats/process'


The **all** flag can be set to return all the stats.
