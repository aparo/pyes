Search
======

The search API allows to execute a search query and get back search hits that match the query. It can be executed across :doc:`indices and types <./indices_types/index>`. The query can either be provided using a simple :doc:`query string as a parameter <./uri_request/index>`, or using a :doc:`request body <./body_request/index>`. 

The search API allows for the following options:


===============================================  ===========================================================================
 Option                                           Description                                                               
===============================================  ===========================================================================
:doc:`query <./query/index>`                     The search query to execute.                                               
:doc:`from / size <./from_size/index>`           From (hit) and the size (number of hits) to return.                        
:doc:`sort <./sort/index>`                       Sort based on different fields including internal ones (like **_score**).  
:doc:`highlighting <./highlighting/index>`       Highlight search results of one or more fields.                            
:doc:`facets <./facets/index>`                   Add one or more facets (aggregated view) as part of the hits.              
:doc:`explain <./explain/index>`                 Explanation on how hits were scored.                                       
:doc:`fields <./fields/index>`                   Return specific *stored* fields per hit.                                   
:doc:`script_fields <./script_fields/index>`     Return script evaluated fields per hit.                                    
:doc:`search_type <./search_type/index>`         The type of search to execute.                                             
:doc:`index_boost <./index_boost/index>`         Allow to specify index level boost when searching across indices.          
:doc:`named_filters <./named_filters/index>`     Allows to return for each hit the filters it matched on.                   
:doc:`scroll <./scroll/index>`                   Scroll a search request.                                                   
===============================================  ===========================================================================

Routing
-------

When executing a search, it will be broadcasted to all the index/indices shards (round robin between replicas). Which shards will be searched on can be controlled by providing the **routing** parameter. For example, when indexing tweets, the routing value can be the user name:  


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/twitter/tweet?routing=kimchy' -d '
    {
        "user" : "kimchy",
        "postDate" : "2009-11-15T14:12:12",
        "message" : "trying out Elastic Search"
    }
    '


In such a case, if we want to search only on the tweets for a specific user, we can specify it as the routing, resulting in the search hitting only the relevant shard:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/twitter/tweet/_search?routing=kimchy' -d '
    {
        "filtered" : {
            "query" : {
                "query_string" : {
                    "query" : "some query string here"
                }
            },
            "filter" : {
                "term" : { "user" : "kimchy" }
            }
        }
    }
    '


The routing parameter can be multi valued represented as a comma separated string. This will result in hitting the relevant shards where the routing values match to.
