.. _es-guide-reference-api-search-query:

=====
Query
=====

The query element within the search request body allows to define a query using the :ref:`Query DSL <es-guide-reference-query-dsl>`.  

.. code-block:: js


    {
        "query" : {
            "term" : { "user" : "kimchy" }
        }
    }


