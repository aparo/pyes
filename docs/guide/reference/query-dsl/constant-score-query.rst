====================
Constant Score Query
====================

A query that wraps a filter and simply returns a constant score equal to the query boost for every document in the filter. Maps to Lucene **ConstantScoreQuery**.


.. code-block:: js


    {
        "constant_score" : {
            "filter" : {
                "term" : { "user" : "kimchy"}
            },
            "boost" : 1.2
        }
    }


The filter object can hold only filter elements, not queries. Filters can be much faster compared to queries since they don't perform any scoring, especially when they are cached.

