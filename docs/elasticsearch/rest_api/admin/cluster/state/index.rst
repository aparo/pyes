Cluster State
=============

The cluster state API allows to get a comprehensive state information of the whole cluster.


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/_cluster/state'


Here is an example cluster state result:


.. code-block:: js


    {
      "cluster_name" : "elasticsearch",
      "master_node" : "9f177403-544d-44b3-9dc4-e2bec3b361df",
      "blocks" : {
      },
      "nodes" : {
        "9f177403-544d-44b3-9dc4-e2bec3b361df" : {
          "name" : "Sunset Bain",
          "transport_address" : "inet[foo.bar.com/127.0.0.1:9300]"
        }
      },
      "metadata" : {
        "indices" : {
          "twitter" : {
            "settings" : {
              "index.number_of_replicas" : "1",
              "index.number_of_shards" : "2"
            },
            "mappings" : {
            },
            "aliases" : [ ]
          }
        }
      },
      "routing_table" : {
        "indices" : {
          "twitter" : {
            "shards" : {
              "0" : [ {
                "state" : "STARTED",
                "primary" : true,
                "node" : "9f177403-544d-44b3-9dc4-e2bec3b361df",
                "relocating_node" : null,
                "shard" : 0,
                "index" : "twitter"
              }, {
                "state" : "UNASSIGNED",
                "primary" : false,
                "node" : null,
                "relocating_node" : null,
                "shard" : 0,
                "index" : "twitter"
              } ],
              "1" : [ {
                "state" : "STARTED",
                "primary" : true,
                "node" : "9f177403-544d-44b3-9dc4-e2bec3b361df",
                "relocating_node" : null,
                "shard" : 1,
                "index" : "twitter"
              }, {
                "state" : "UNASSIGNED",
                "primary" : false,
                "node" : null,
                "relocating_node" : null,
                "shard" : 1,
                "index" : "twitter"
              } ]
            }
          }
        }
      },
      "routing_nodes" : {
        "unassigned" : [ {
          "state" : "UNASSIGNED",
          "primary" : false,
          "node" : null,
          "relocating_node" : null,
          "shard" : 0,
          "index" : "twitter"
        }, {
          "state" : "UNASSIGNED",
          "primary" : false,
          "node" : null,
          "relocating_node" : null,
          "shard" : 1,
          "index" : "twitter"
        } ],
        "nodes" : {
          "9f177403-544d-44b3-9dc4-e2bec3b361df" : [ {
            "state" : "STARTED",
            "primary" : true,
            "node" : "9f177403-544d-44b3-9dc4-e2bec3b361df",
            "relocating_node" : null,
            "shard" : 0,
            "index" : "twitter"
          }, {
            "state" : "STARTED",
            "primary" : true,
            "node" : "9f177403-544d-44b3-9dc4-e2bec3b361df",
            "relocating_node" : null,
            "shard" : 1,
            "index" : "twitter"
          } ]
        }
      }
    }


Response Filters
----------------

It is possible to filter the cluster state response using the following REST parameters:


===========================  ==============================================================================================
 Parameter                    Description                                                                                  
===========================  ==============================================================================================
**filter_nodes**              Set to **true** to filter out the **nodes** part of the response.                            
**filter_routing_table**      Set to **true** to filter out the **routing_table** part of the response.                    
**filter_metadata**           Set to **true** to filter out the **metadata** part of the response.                         
**filter_indices**            When not filtering metadata, a comma separated list of indices to include in the response.   
===========================  ==============================================================================================

Example follows:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/_cluster/state?filter_nodes=true'

