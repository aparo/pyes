.. _es-guide-reference-api-search-facets-filter-facet:

============
Filter Facet
============

A facet filter allows to return a count of the hits matching the facet filter. The filter itself can be expressed using the :ref:`Query DSL <es-guide-reference-query-dsl>`.  For example:


.. code-block:: js


    {
        "facets" : {
            "wow_facet" : {
                "filter" : {
                    "term" : { "tag" : "wow" }
                }
            }
        }
    }    


Note, facet filters are faster than query facet when using native filters (non query wrapper ones).

