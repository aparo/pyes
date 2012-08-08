.. _es-guide-reference-api-search-request-body:

============
Request Body
============

The search request can be executed with a search DSL, which includes the :ref:`Query DSL <es-guide-reference-query-dsl>`,  within its body. Here is an example:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/twitter/tweet/_search' -d '{
        "query" : {
            "term" : { "user" : "kimchy" }
        }
    }
    '


And here is a sample response:


.. code-block:: js


    {
        "_shards":{
            "total" : 5,
            "successful" : 5,
            "failed" : 0
        },
        "hits":{
            "total" : 1,
            "hits" : [
                {
                    "_index" : "twitter",
                    "_type" : "tweet",
                    "_id" : "1", 
                    "_source" : {
                        "user" : "kimchy",
                        "postDate" : "2009-11-15T14:12:12",
                        "message" : "trying out Elastic Search"
                    }
                }
            ]
        }
    }



Parameters
==========

===================  ==========================================================================================================================================================================================
 Name                 Description                                                                                                                                                                              
===================  ==========================================================================================================================================================================================
 **timeout**          A search timeout, bounding the search request to be executed within the specified time value and bail with the hits accumulated up to that point when expired. Defaults to no timeout.   
 **from**             The starting from index of the hits to return. Defaults to **0**.                                                                                                                        
 **size**             The number of hits to return. Defaults to **10**.                                                                                                                                        
 **search_type**      The type of the search operation to perform. Can be **dfs_query_then_fetch**, **dfs_query_and_fetch**, **query_then_fetch**, **query_and_fetch**. Defaults to **query_then_fetch**.      
===================  ==========================================================================================================================================================================================

Out of the above, the **search_type** is the one that can not be passed within the search request body, and in order to set it, it must be passed as a request REST parameter.


The rest of the search request should be passed within the body itself. The body content can also be passed as a REST parameter named **source**.


Note
    Both HTTP GET and HTTP POST can be used to execute search with body. Since not all clients support GET with body, POST is allowed as well.

