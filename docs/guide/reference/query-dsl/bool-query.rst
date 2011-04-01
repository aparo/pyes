.. _es-guide-reference-query-dsl-bool-query:

==========
Bool Query
==========

A query that matches documents matching boolean combinations of other queries. The bool query maps to Lucene **BooleanQuery**. It is built using one or more boolean clauses, each clause with a typed occurrence. The occurrence types are:


================  ========================================================================================================================================================================================================================================================================
 Occur             Description                                                                                                                                                                                                                                                            
================  ========================================================================================================================================================================================================================================================================
 **must**          The clause (query) must appear in matching documents.                                                                                                                                                                                                                  
 **should**        The clause (query) should appear in the matching document. A boolean query with no **must** clauses, one or more **should** clauses must match a document. The minimum number of should clauses to match can be set using **minimum_number_should_match** parameter.   
 **must_not**      The clause (query) must not appear in the matching documents. Note that it is not possible to search on documents that only consists of a **must_not** clauses.                                                                                                        
================  ========================================================================================================================================================================================================================================================================

The bool query also supports **disable_coord** parameter (defaults to **false**).


.. code-block:: js


    {
        "bool" : {
            "must" : {
                "term" : { "user" : "kimchy" }
            },
            "must_not" : {
                "range" : {
                    "age" : { "from" : 10, "to" : 20 }
                }
            },
            "should" : [
                {
                    "term" : { "tag" : "wow" }
                },
                {
                    "term" : { "tag" : "elasticsearch" }
                }
            ],
            "minimum_number_should_match" : 1,
            "boost" : 1.0
        }
    }


