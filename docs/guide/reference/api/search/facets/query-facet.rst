.. _es-guide-reference-api-search-facets-query-facet:

===========
Query Facet
===========

A facet query allows to return a count of the hits matching the facet query. The query itself can be expressed using the Query DSL. For example:


.. code-block:: js


    {
        "facets" : {
            "wow_facet" : {
                "query" : {
                    "term" : { "tag" : "wow" }
                }
            }
        }
    }    

