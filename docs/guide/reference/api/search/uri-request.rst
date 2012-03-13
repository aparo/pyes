.. _es-guide-reference-api-search-uri-request:

===========
Uri Request
===========

A search request can be executed purely using a URI by providing request parameters. Not all search options are exposed when executing a search using this mode, but it can be handy for quick "curl tests". Here is an example:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/twitter/tweet/_search?q=user:kimchy'


And here is a sample response:


.. code-block:: js


    {
        :ref:`_shards <es-guide-reference-api-search-{>`  s <es-guide-reference-api-search-{>`  
            "total" : 5,
            "successful" : 5,
            "failed" : 0
        },
        :ref:`hits <es-guide-reference-api-search-{>`  s <es-guide-reference-api-search-{>`  
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

The parameters allowed in the URI are:


==================  ================================================================================================================================================================================================================================================================================================================
 Name                Description                                                                                                                                                                                                                                                                                                    
==================  ================================================================================================================================================================================================================================================================================================================
q                    The query string (maps to the **query_string** query).                                                                                                                                                                                                                                                         
df                   The default field to use when no field prefix is defined within the query.                                                                                                                                                                                                                                     
analyzer             The analyzer name to be used when analyzing the query string.                                                                                                                                                                                                                                                  
default_operator     The default operator to be used, can be **AND** or **OR**. Defaults to **OR**.                                                                                                                                                                                                                                 
explain              For each hit, contain an explanation of how scoring of the hits was computed.                                                                                                                                                                                                                                  
fields               The selective fields of the document to return for each hit (either retried from the index if stored, or from the **_source** if not), comma delimited. Defaults to the internal **_source** field. Not specifying any value will cause no fields to return.                                                   
sort                 Sorting to perform. Can either be in the form of **fieldName**, or **fieldName:asc**/**fieldName:desc**. The fieldName can either be an actual field within the document, or the special **_score** name to indicate sorting based on scores. There can be several **sort** parameters (order is important).   
track_scores        When sorting, set to **true** in order to still track scores and return them as part of each hit.                                                                                                                                                                                                               
timeout              A search timeout, bounding the search request to be executed within the specified time value and bail with the hits accumulated up to that point when expired. Defaults to no timeout.                                                                                                                         
from                 The starting from index of the hits to return. Defaults to **0**.                                                                                                                                                                                                                                              
size                 The number of hits to return. Defaults to **10**.                                                                                                                                                                                                                                                              
search_type          The type of the search operation to perform. Can be **dfs_query_then_fetch**, **dfs_query_and_fetch**, **query_then_fetch**, **query_and_fetch**. Defaults to **query_then_fetch**.                                                                                                                            
==================  ================================================================================================================================================================================================================================================================================================================

