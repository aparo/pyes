.. _es-guide-reference-query-dsl-flt-field-query:

===============
Flt Field Query
===============

The **fuzzy_like_this_field** query is the same as the **fuzzy_like_this** query, except that it runs against a single field. It provides nicer query DSL over the generic **fuzzy_like_this** query, and support typed fields query (automatically wraps typed fields with type filter to match only on the specific type).


.. code-block:: js


    {
        "fuzzy_like_this_field" : {
            "name.first" : {
                "like_text" : "text like this one",
                "max_query_terms" : 12
            }
        }
    }


Note
    **fuzzy_like_this_field** can be shortened to **flt_field**.


The **fuzzy_like_this_field** top level parameters include:


=====================  =========================================================================================================
 Parameter              Description                                                                                             
=====================  =========================================================================================================
**like_text**          The text to find documents like it, *required*.                                                          
**ignore_tf**          Should term frequency be ignored. Defaults to **false**.                                                 
**max_query_terms**    The maximum number of query terms that will be included in any generated query. Defaults to **25**.      
**min_similarity**     The minimum similarity of the term variants. Defaults to **0.5**.                                        
**prefix_length**      Length of required common prefix on variant terms. Defaults to **0**.                                    
**boost**              Sets the boost value of the query. Defaults to **1.0**.                                                  
**analyzer**           The analyzer that will be used to analyze the text. Defaults to the analyzer associated with the field.  
=====================  =========================================================================================================
