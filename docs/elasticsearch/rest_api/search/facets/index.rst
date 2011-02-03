Facets
======

Facets allow to provide aggregated data based on the search request. For example, a facet can return the most popular terms within the search query.


===================================================  ============================================================================================
 Facet                                                Description                                                                                
===================================================  ============================================================================================
:doc:`query <./query_facet/index>`                   A facet returning a count matching the facet query.                                         
:doc:`filter <./filter_facet/index>`                 A facet returning a count matching the facet filter.                                        
:doc:`terms <./terms_facet/index>`                   A facet returning the N most frequent terms.                                                
:doc:`histogram <./histogram_facet/index>`           A histogram facet across numeric fields.                                                    
:doc:`statistical <./statistical_facet/index>`       Compute statistical data for numeric fields or scripts.                                     
:doc:`range <./range_facet/index>`                   A facet computing counts and totals for documents falling within specific range.            
:doc:`geo_distance <./geo_distance_facet/index>`     A facet computing counts and totals for documents falling within specific range distances.  
===================================================  ============================================================================================

score / global
--------------

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
------

All facets can be configured with an additional filter (explained in the :doc:`Query DSL <./../../query_dsl#Filters/index>` section), which will further reduce the documents they execute on. For example:


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

