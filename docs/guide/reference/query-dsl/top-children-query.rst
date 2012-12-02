.. _es-guide-reference-query-dsl-top-children-query:

==================
Top Children Query
==================

The **top_children** query runs the child query with an estimated hits size, and out of the hit docs, aggregates it into parent docs. If there aren't enough parent docs matching the requested from/size search request, then it is run again with a wider (more hits) search.


The **top_children** also provide scoring capabilities, with the ability to specify **max**, **sum** or **avg** as the score type.


One downside of using the **top_children** is that if there are more child docs matching the required hits when executing the child query, then the **total_hits** result of the search response will be incorrect.


How many hits are asked for in the first child query run is controlled using the **factor** parameter (defaults to **5**). For example, when asking for 10 parent docs (with **from** set to 0), then the child query will execute with 50 hits expected. If not enough parents are found (in our example 10), and there are still more child docs to query, then the child search hits are expanded by multiplying by the **incremental_factor** (defaults to **2**). 


The required parameters are the **query** and **type** (the child type to execute the query on). Here is an example with all different parameters, including the default values:


.. code-block:: js


    {
        "top_children" : {
            :ref:`type <es-guide-reference-query-dsl>`  pe <es-guide-reference-query-dsl>`  "blog_tag",
            "query" : {
                "term" : {
                    "tag" : "something"
                }
            }
            "score" : "max",
            "factor" : 5,
            "incremental_factor" : 2
        }
    }


Scope
=====

A **_scope** can be defined on the query allowing to run facets on the same scope name that will work against the child documents. For example:


.. code-block:: js


    {
        "top_children" : {
            "_scope" : "my_scope",
            :ref:`type <es-guide-reference-query-dsl>`  pe <es-guide-reference-query-dsl>`  "blog_tag",
            "query" : {
                "term" : {
                    "tag" : "something"
                }
            }
        }
    }


Memory Considerations
=====================

With the current implementation, all **_id** values are loaded to memory (heap) in order to support fast lookups, so make sure there is enough mem for it.

