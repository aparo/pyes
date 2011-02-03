Fuzzy Like This Query
=====================

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


=====================  =====================================================================================================
 Parameter              Description                                                                                         
=====================  =====================================================================================================
**fields**             A list of the fields to run the more like this query against. Defaults to the **_all** field.        
**like_text**          The text to find documents like it, *required*.                                                      
**ignore_tf**          Should term frequency be ignored. Defaults to **false**.                                             
**max_query_terms**    The maximum number of query terms that will be included in any generated query. Defaults to **25**.  
**boost**              Sets the boost value of the query. Defaults to **1.0**.                                              
=====================  =====================================================================================================
