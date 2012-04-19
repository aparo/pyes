.. _es-guide-reference-query-dsl-query-string-query:

==================
Query String Query
==================

A query that uses a query parser in order to parse its content. Here is an example:


.. code-block:: js


    {
        "query_string" : {
            "default_field" : "content",
            "query" : "this AND that OR thus"
        }
    }


The **query_string** top level parameters include:


====================================  ======================================================================================================================================================================================================================================================================================================================================
 Parameter                             Description                                                                                                                                                                                                                                                                                                                          
====================================  ======================================================================================================================================================================================================================================================================================================================================
 **query**                             The actual query to be parsed.                                                                                                                                                                                                                                                                                                       
 **default_field**                     The default field for query terms if no prefix field is specified. Defaults to the **_all** field.                                                                                                                                                                                                                                   
 **default_operator**                  The default operator used if no explicit operator is specified. For example, with a default operator of **OR**, the query **capital of Hungary** is translated to **capital OR of OR Hungary**, and with default operator of **AND**, the same query is translated to **capital AND of AND Hungary**. The default value is **OR**.   
 **analyzer**                          The analyzer name used to analyze the query string.                                                                                                                                                                                                                                                                                  
 **allow_leading_wildcard**            When set, ***** or **?** are allowed as the first character. Defaults to **true**.                                                                                                                                                                                                                                                   
 **lowercase_expanded_terms**          Whether terms of wildcard, prefix, fuzzy, and range queries are to be automatically lower-cased or not (since they are not analyzed). Default it **true**.                                                                                                                                                                           
 **enable_position_increments**        Set to **true** to enable position increments in result queries. Defaults to **true**.                                                                                                                                                                                                                                               
 **fuzzy_prefix_length**               Set the prefix length for fuzzy queries. Default is **0**.                                                                                                                                                                                                                                                                           
 **fuzzy_min_sim**                     Set the minimum similarity for fuzzy queries. Defaults to **0.5**                                                                                                                                                                                                                                                                    
 **phrase_slop**                       Sets the default slop for phrases. If zero, then exact phrase matches are required.  Default value is **0**.                                                                                                                                                                                                                         
 **boost**                             Sets the boost value of the query. Defaults to **1.0**.                                                                                                                                                                                                                                                                              
 **analyze_wildcard**                  By default, wildcards terms in a query string are not analyzed. By setting this value to **true**, a best effort will be made to analyze those as well.                                                                                                                                                                              
 **auto_generate_phrase_queries**      Default to **false**.                                                                                                                                                                                                                                                                                                                
====================================  ======================================================================================================================================================================================================================================================================================================================================

Multi Field
===========

The **query_string** query can also run against multiple fields. The idea of running the **query_string** query against multiple fields is by internally creating several queries for the same query string, each with **default_field** that match the fields provided. Since several queries are generated, combining them can be automatically done either using a **dis_max** query or a simple **bool** query. For example (the **name** is boosted by 5 using **^5** notation):


.. code-block:: js


    {
        "query_string" : {
            "fields" : ["content", "name^5"],
            "query" : "this AND that OR thus",
            "use_dis_max" : true
        }
    }


When running the **query_string** query against multiple fields, the following additional parameters are allowed:


===================  ==========================================================================================================================================
 Parameter            Description                                                                                                                              
===================  ==========================================================================================================================================
 **use_dis_max**      Should the queries be combined using **dis_max** (set it to **true**), or a **bool** query (set it to **false**). Defaults to **true**.  
 **tie_breaker**      When using **dis_max**, the disjunction max tie breaker. Defaults to **0**.                                                              
===================  ==========================================================================================================================================

The fields parameter can also include pattern based field names, allowing to automatically expand to the relevant fields (dynamically introduced fields included). For example:


.. code-block:: js


    {
        "query_string" : {
            "fields" : ["content", "name.*^5"],
            "query" : "this AND that OR thus",
            "use_dis_max" : true
        }
    }


h1(#Syntax_Extension). Syntax Extension

There are several syntax extensions to the Lucene query language.


missing / exists
----------------

The **_exists_** and **_missing_** syntax allows to control docs that have fields that exists within them (have a value) and missing. The syntax is: **_exists_:field1**, **_missing_:field** and can be used anywhere a query string is used.

