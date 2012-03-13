.. _es-guide-reference-query-dsl-nested-query:

============
Nested Query
============

Nested query allows to query nested objects / docs (see :ref:`nested mapping <es-guide-reference-mapping-nested-type>`.  The query is executed against the nested objects / docs as if they were indexed as separate docs (they are, internally) and resulting in the root parent doc (or parent nested mapping). Here is a sample mapping we will work with:


.. code-block:: js


    {
        "type1" : {
            "properties" : {
                "obj1" : {
                    "type" : "nested"
                }
            }
        }
    }


And here is a sample nested query usage:


.. code-block:: js


    {
        "nested" : {
            "path" : "obj1",
            "score_mode" : "avg",
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
            }
        }
    }


The query **path** points to the nested object path, and the **query** (or **filter**) includes the query that will run on the nested docs matching the direct path, and joining with the root parent docs.


The **score_mode** allows to set how inner children matching affects scoring of parent. It defaults to **avg**, but can be **total**, **max** and **none**.


Multi level nesting is automatically supported, and detected, resulting in an inner nested query to automatically match the relevant nesting level (and not root) if it exists within another nested query.
