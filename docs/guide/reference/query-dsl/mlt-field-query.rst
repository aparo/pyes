.. _es-guide-reference-query-dsl-mlt-field-query:

===============
Mlt Field Query
===============

The **more_like_this_field** query is the same as the **more_like_this** query, except it runs against a single field. It provides nicer query DSL over the generic **more_like_this** query, and support typed fields query (automatically wraps typed fields with type filter to match only on the specific type).


.. code-block:: js


    {
        "more_like_this_field" : {
            "name.first" : {
                "like_text" : "text like this one",
                "min_term_freq" : 1,
                "max_query_terms" : 12
            }
        }
    }


Note
    **more_like_this_field** can be shortened to **mlt_field**.


The **more_like_this_field** top level parameters include:


============================  ================================================================================================================================================================================================================================================================================================================
 Parameter                     Description                                                                                                                                                                                                                                                                                                    
============================  ================================================================================================================================================================================================================================================================================================================
**like_text**                 The text to find documents like it, *required*.                                                                                                                                                                                                                                                                 
**percent_terms_to_match**    The percentage of terms to match on (float value). Defaults to **0.3** (30 percent).                                                                                                                                                                                                                            
**min_term_freq**             The frequency below which terms will be ignored in the source doc. The default frequency is **2**.                                                                                                                                                                                                              
**max_query_terms**           The maximum number of query terms that will be included in any generated query. Defaults to **25**.                                                                                                                                                                                                             
**stop_words**                An array of stop words. Any word in this set is considered "uninteresting" and ignored. Even if your Analyzer allows stopwords, you might want to tell the MoreLikeThis code to ignore them, as for the purposes of document similarity it seems reasonable to assume that "a stop word is never interesting".  
**min_doc_freq**              The frequency at which words will be ignored which do not occur in at least this many docs. Defaults to **5**.                                                                                                                                                                                                  
**max_doc_freq**              The maximum frequency in which words may still appear. Words that appear in more than this many docs will be ignored. Defaults to unbounded.                                                                                                                                                                    
**min_word_len**              The minimum word length below which words will be ignored. Defaults to **0**.                                                                                                                                                                                                                                   
**max_word_len**              The maximum word length above which words will be ignored. Defaults to unbounded (**0**).                                                                                                                                                                                                                       
**boost_terms**               Sets the boost factor to use when boosting terms. Defaults to **1**.                                                                                                                                                                                                                                            
**boost**                     Sets the boost value of the query. Defaults to **1.0**.                                                                                                                                                                                                                                                         
**analyzer**                  The analyzer that will be used to analyze the text. Defaults to the analyzer associated with the field.                                                                                                                                                                                                         
============================  ================================================================================================================================================================================================================================================================================================================
