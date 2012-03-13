.. _es-guide-reference-query-dsl-mlt-query:

=========
Mlt Query
=========

More like this query find documents that are "like" provided text by running it against one or more fields.


.. code-block:: js


    {
        "more_like_this" : {
            "fields" : ["name.first", "name.last"],
            "like_text" : "text like this one",
            "min_term_freq" : 1,
            "max_query_terms" : 12
        }
    }


Note
    **more_like_this** can be shortened to **mlt**.


The **more_like_this** top level parameters include:


============================  ================================================================================================================================================================================================================================================================================================================
 Parameter                     Description                                                                                                                                                                                                                                                                                                    
============================  ================================================================================================================================================================================================================================================================================================================
**fields**                    A list of the fields to run the more like this query against. Defaults to the **_all** field.                                                                                                                                                                                                                   
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
