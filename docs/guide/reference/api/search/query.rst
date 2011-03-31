=====
Query
=====

The query element within the search request body allows to define a query using the :doc:`Query DSL <.//guide/reference/query-dsl>`.  

.. code-block:: js


    {
        "query" : {
            "term" : { "user" : "kimchy" }
        }
    }


