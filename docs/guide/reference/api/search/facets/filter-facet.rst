.. _es-guide-reference-api-search-facets-filter-facet:

============
Filter Facet
============

A filter facet (not to be confused with a :ref:`facet filter <es-guide-reference-api-search-facets-index>`  allows you to return a count of the hits matching the filter. The filter itself can be expressed using the :ref:`Query DSL <es-guide-reference-query-dsl>`.  For example:


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


Note, filter facet filters are faster than query facet when using native filters (non query wrapper ones).

