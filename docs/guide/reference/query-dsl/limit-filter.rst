.. _es-guide-reference-query-dsl-limit-filter:

============
Limit Filter
============

A limit filter limits the number of documents (per shard) to execute on. For example:


.. code-block:: js


    {
        "filtered" : {
            "filter" : {
                 "limit" : {"value" : 100}
             },
             "query" : {
                "term" : { "name.first" : "shay" }
            }
        }
    }

