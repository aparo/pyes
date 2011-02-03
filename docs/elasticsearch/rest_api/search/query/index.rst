Query
=====

The query element within the search request body allows to define a query using the :doc:`Query DSL <.//../query_dsl/index>`. 

.. code-block:: js


    {
        "query" : {
            "term" : { "user" : "kimchy" }
        }
    }


