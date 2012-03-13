.. _es-guide-reference-api-admin-cluster-nodes-info:

========================
Admin Cluster Nodes Info
========================

The cluster nodes info API allows to retrieve one or more (or all) of the cluster nodes information.


.. code-block:: bash

    curl -XGET 'http://localhost:9200/_cluster/nodes'
    curl -XGET 'http://localhost:9200/_cluster/nodes/nodeId1,nodeId2'
    
    # Shorter Format
    curl -XGET 'http://localhost:9200/_nodes'
    curl -XGET 'http://localhost:9200/_nodes/nodeId1,nodeId2'


The first command retrieves information of all the nodes in the cluster. The second command selectively retrieves nodes information of only **nodeId1** and **nodeId2**. All the nodes selective options are explained :ref:`here <es-guide-reference-api-index>`.  

By default, it just returns the attributes and core settings for a node. It also allows to get information on **settings**, **os**, **process**, **jvm**, **thread_pool**, **network**, **transport** and **http**:


.. code-block:: bash

    curl -XGET 'http://localhost:9200/_nodes?os=true&process=true'
    curl -XGET 'http://localhost:9200/_nodes/10.0.0.1/?os=true&process=true'
    
    # Or, specific type endpoint:
    
    curl -XGET 'http://localhost:9200/_nodes/process'
    curl -XGET 'http://localhost:9200/_nodes/10.0.0.1/process'

