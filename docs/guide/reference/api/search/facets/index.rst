.. _es-guide-reference-api-search-facets-index:

======
Facets
======

Facets allow to provide aggregated data based on the search request. For example, a facet can return the most popular terms within the search query.


score / global
==============

All facets can be configured to run within a specific scope. The two common ones are **_main_** and **_global_**. The **_main_** scope causes the facet to be bounded to the current search query, while the **_global_** scope executes the facet globally (not bounded by the search query, though, of course, can still be filtered).


A shorthand to set a facet to run globally is to set the **global** parameter to **true**:


.. code-block:: js


    {
        "facets" : {
            "wow_facet" : {
                "facet_type" : {
                    ...
                },
                "global" : true
            }
        }
    }    


Custom scope names works in conjunction with child queries / filters, allowing to force the facets to run on the child documents matching the child specific query.


filter
======

All facets can be configured with an additional filter (explained in the :ref:`Query DSL <es-guide-reference-api-search-facets-guide-reference-query-dsl>`  section), which will further reduce the documents they execute on. For example:


.. code-block:: js


    {
        "facets" : {
            "wow_facet" : {
                "facet_type" : {
                    ...
                },
                "facet_filter" : {
                    "term" : { "user" : "kimchy"}
                }
            }
        }
    }    

