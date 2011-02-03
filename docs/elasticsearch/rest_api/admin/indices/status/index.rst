Indices Status
==============

The indices status API allows to get a comprehensive status information of one or more indices.


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/twitter/_status'


Here is an example status result:


.. code-block:: js


    {
      "ok" : true,
      "_shards" : {
        "total" : 4,
        "successful" : 4,
        "failed" : 0
      },
      "indices" : {
        "twitter" : {
          "aliases" : [ ],
          "settings" : {
            "index.number_of_replicas" : "1",
            "index.number_of_shards" : "2"
          },
          "store_size" : "1.7kb",
          "store_size_in_bytes" : 1776,
          "estimated_flushable_memory_size" : "0b",
          "estimated_flushable_memory_size_in_bytes" : 0,
          "translog_operations" : 2,
          "docs" : {
            "num_docs" : 1,
            "max_doc" : 1,
            "deleted_docs" : 0
          },
          "shards" : {
            "0" : [ {
              "routing" : {
                "state" : "STARTED",
                "primary" : true,
                "node" : "5dad331d-7c16-4ae3-bb83-3b9c67b981dc",
                "relocating_node" : null,
                "shard" : 0,
                "index" : "twitter"
              },
              "state" : "STARTED",
              "store_size" : "52b",
              "store_size_in_bytes" : 52,
              "estimated_flushable_memory_size" : "0b",
              "estimated_flushable_memory_size_in_bytes" : 0,
              "translog_id" : 1281989629222,
              "translog_operations" : 0,
              "docs" : {
                "num_docs" : 0,
                "max_doc" : 0,
                "deleted_docs" : 0
              }
            }, {
              "routing" : {
                "state" : "STARTED",
                "primary" : false,
                "node" : "260c5cbd-a4f7-4b8d-95fc-9cc558ef8ac6",
                "relocating_node" : null,
                "shard" : 0,
                "index" : "twitter"
              },
              "state" : "STARTED",
              "store_size" : "32b",
              "store_size_in_bytes" : 32,
              "estimated_flushable_memory_size" : "0b",
              "estimated_flushable_memory_size_in_bytes" : 0,
              "translog_id" : 1281989629222,
              "translog_operations" : 0,
              "docs" : {
                "num_docs" : 0,
                "max_doc" : 0,
                "deleted_docs" : 0
              }
            } ],
            "1" : [ {
              "routing" : {
                "state" : "STARTED",
                "primary" : true,
                "node" : "5dad331d-7c16-4ae3-bb83-3b9c67b981dc",
                "relocating_node" : null,
                "shard" : 1,
                "index" : "twitter"
              },
              "state" : "STARTED",
              "store_size" : "856b",
              "store_size_in_bytes" : 856,
              "estimated_flushable_memory_size" : "0b",
              "estimated_flushable_memory_size_in_bytes" : 0,
              "translog_id" : 1281989629239,
              "translog_operations" : 1,
              "docs" : {
                "num_docs" : 1,
                "max_doc" : 1,
                "deleted_docs" : 0
              }
            }, {
              "routing" : {
                "state" : "STARTED",
                "primary" : false,
                "node" : "260c5cbd-a4f7-4b8d-95fc-9cc558ef8ac6",
                "relocating_node" : null,
                "shard" : 1,
                "index" : "twitter"
              },
              "state" : "STARTED",
              "store_size" : "836b",
              "store_size_in_bytes" : 836,
              "estimated_flushable_memory_size" : "0b",
              "estimated_flushable_memory_size_in_bytes" : 0,
              "translog_id" : 1281989629239,
              "translog_operations" : 1,
              "docs" : {
                "num_docs" : 1,
                "max_doc" : 1,
                "deleted_docs" : 0
              }
            } ]
          }
        }
      }
    }



Multi Index
-----------

The status API can be applied to more than one index with a single call, or even on **_all** the indices.


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/kimchy,elasticsearch/_status'
    
    $ curl -XGET 'http://localhost:9200/_status'

