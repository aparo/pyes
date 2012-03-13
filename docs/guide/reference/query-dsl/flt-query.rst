.. _es-guide-reference-query-dsl-flt-query:

=========
Flt Query
=========

Fuzzy like this query find documents that are "like" provided text by running it against one or more fields.


.. code-block:: js


    {
        "fuzzy_like_this" : {
            "fields" : ["name.first", "name.last"],
            "like_text" : "text like this one",
            "max_query_terms" : 12
        }
    }


Note
    **fuzzy_like_this** can be shortened to **flt**.


The **fuzzy_like_this** top level parameters include:


=====================  =========================================================================================================
 Parameter              Description                                                                                             
=====================  =========================================================================================================
**fields**             A list of the fields to run the more like this query against. Defaults to the **_all** field.            
**like_text**          The text to find documents like it, *required*.                                                          
**ignore_tf**          Should term frequency be ignored. Defaults to **false**.                                                 
**max_query_terms**    The maximum number of query terms that will be included in any generated query. Defaults to **25**.      
**min_similarity**     The minimum similarity of the term variants. Defaults to **0.5**.                                        
**prefix_length**      Length of required common prefix on variant terms. Defaults to **0**.                                    
**boost**              Sets the boost value of the query. Defaults to **1.0**.                                                  
**analyzer**           The analyzer that will be used to analyze the text. Defaults to the analyzer associated with the field.  
=====================  =========================================================================================================

How it Works
============

Fuzzifies ALL terms provided as strings and then picks the best n differentiating terms. In effect this mixes the behaviour of FuzzyQuery and MoreLikeThis but with special consideration of fuzzy scoring factors. This generally produces good results for queries where users may provide details in a number offields and have no knowledge of boolean query syntax and also want a degree of fuzzy matching and a fast query.


For each source term the fuzzy variants are held in a BooleanQuery with no coord factor (because we are not looking for matches on multiple variants in any one doc). Additionally, a specialized TermQuery is used for variants and does not use that variant term's IDF because this would favour rarer terms eg misspellings. Instead, all variants use the same IDF ranking (the one for the source query term) and this is factored into the variant's boost. If the source query term does not exist in the index the average IDF of the variants is used.

