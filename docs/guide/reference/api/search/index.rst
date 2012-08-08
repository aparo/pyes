.. _es-guide-reference-api-search-index:
.. _es-guide-reference-api-search:

======
Search
======

The search API allows to execute a search query and get back search hits that match the query. It can be executed across :ref:`indices and types <es-guide-reference-api-search-indices-types>`.  The query can either be provided using a simple :ref:`query string as a parameter <es-guide-reference-api-search-uri-request>`,  or using a :ref:`request body <es-guide-reference-api-search-request-body>`.  

Routing
=======

When executing a search, it will be broadcasted to all the index/indices shards (round robin between replicas). Which shards will be searched on can be controlled by providing the **routing** parameter. For example, when indexing tweets, the routing value can be the user name:


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/twitter/tweet?routing=kimchy' -d '{
        "user" : "kimchy",
        "postDate" : "2009-11-15T14:12:12",
        "message" : "trying out Elastic Search"
    }
    '


In such a case, if we want to search only on the tweets for a specific user, we can specify it as the routing, resulting in the search hitting only the relevant shard:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/twitter/tweet/_search?routing=kimchy' -d '{
        "query": {
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
    }
    '


The routing parameter can be multi valued represented as a comma separated string. This will result in hitting the relevant shards where the routing values match to.


Stats Groups
============

A search can be associated with stats groups, which maintains a statistics aggregation per group. It can later be retrieved using the indices stats API specifically. For example, here is a search body request that associate the request with two different groups:


.. code-block:: js

    {
        "query" : {
            "match_all" : {}
        },
        "stats" : ["group1", "group2"]
    }

.. toctree::
    :maxdepth: 1

    explain
    facets/index
    fields
    filter
    from-size
    highlighting
    index-boost
    indices-types
    named-filters
    min-score
    query
    preference
    request-body
    script-fields
    scroll
    search-type
    sort
    uri-request
    version