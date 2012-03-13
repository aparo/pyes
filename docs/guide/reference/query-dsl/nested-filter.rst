.. _es-guide-reference-query-dsl-nested-filter:

=============
Nested Filter
=============

A **nested** filter, works in a similar fashion to the :ref:`nested <es-guide-reference-query-dsl-nested-query>`  query, except used as a filter. It follows exactly the same structure, but also allows to cache the results (set **_cache** to **true**), and have it named (set the **_name** value). For example:


.. code-block:: js


    {
        "filtered" : {
            "query" : { "match_all" : {} },
            "filter" : {
                "nested" : {
                    "path" : "obj1",
                    "query" : {
                        "bool" : {
                            "must" : [
                                {
                                    "text" : {"obj1.name" : "blue"}
                                },
                                {
                                    "range" : {"obj1.count" : {"gt" : 5}}
                                }
                            ]
                        }
                    },
                    "_cache" : true
                }
            }
        }
    }

