.. _es-guide-reference-api-admin-cluster-state:

===================
Admin Cluster State
===================

The cluster state API allows to get a comprehensive state information of the whole cluster.


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/_cluster/state'


Response Filters
================

It is possible to filter the cluster state response using the following REST parameters:


======================  ==============================================================================================
 Parameter               Description                                                                                  
======================  ==============================================================================================
filter_nodes             Set to **true** to filter out the **nodes** part of the response.                            
filter_routing_table     Set to **true** to filter out the **routing_table** part of the response.                    
filter_metadata          Set to **true** to filter out the **metadata** part of the response.                         
filter_blocks            Set to **true** to filter out the **blocks** part of the response.                           
filter_indices           When not filtering metadata, a comma separated list of indices to include in the response.   
======================  ==============================================================================================

Example follows:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/_cluster/state?filter_nodes=true'

