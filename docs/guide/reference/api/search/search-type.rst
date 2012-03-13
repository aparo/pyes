.. _es-guide-reference-api-search-search-type:

===========
Search Type
===========

There are different execution paths that can be done when executing a distributed search. The distributed search operation needs to be scattered to all the relevant shards and then all the results are gathered back. When doing scatter/gather type execution, there are several ways to do that, specifically with search engines.


One of the questions when executing a distributed search is how much results to retrieve from each shard. For example, if we have 10 shards, the 1st shard might hold the most relevant results from 0 till 10, with other shards results ranking below it. For this reason, when executing a request, we will need to get results from 0 till 10 from all shards, sort them, and then return the results if we want to insure correct results.


Another question, which relates to search engine, is the fact that each shard stands on its own. When a query is executed on a specific shard, it does not take into account term frequencies and other search engine information from the other shards. If we want to support accurate ranking, we would need to first execute the query against all shards and gather the relevant term frequencies, and then, based on it, execute the query.


Also, because of the need to sort the results, getting back a large document set, or even scrolling it, while maintaing the correct sorting behavior can be a very expensive operation. For large result set scrolling without sorting, the **scan** search type (explained below) is also available.


ElasticSearch is very flexible and allows to control the type of search to execute on a *per search request* basis.  The type can be configured by setting the *search_type* parameter in the query string. The types are:


Query And Fetch
===============

Parameter value: *query_and_fetch*.


The most naive (and possibly fastest) implementation is to simply execute the query on all relevant shards and return the results. Each shard returns **size** results. Since each shard already returns **size** hits, this type actually returns **size** times **number of shards** results back to the caller.


Query Then Fetch
================

Parameter value: *query_then_fetch*.


The query is executed against all shards, but only enough information is returned (*not the document content*). The results are then sorted and ranked, and based on it, *only the relevant shards* are asked for the actual document content. The return number of hits is exactly as specified in **size**, since they are the only ones that are fetched. This is very handy when the index has a lot of shards (not replicas, shard id groups).


Dfs, Query And Fetch
====================

Parameter value: *dfs_query_and_fetch*.


Same as "Query And Fetch", except for an initial scatter phase which goes and computes the distributed term frequencies for more accurate scoring.


Dfs, Query Then Fetch
=====================

Parameter value: *dfs_query_then_fetch*.


Same as "Query Then Fetch", except for an initial scatter phase which goes and computes the distributed term frequencies for more accurate scoring.


Count
=====

Parameter value: *count*.


A special search type that returns the count that matched the search request without any docs (represented in **total_hits**), and possibly, including facets as well. In general, this is preferable to the **count** API as it provides more options.


Scan
====

Parameter value: *scan*.


The **scan** search type allows to efficiently scroll a large result set. Its used first by executing a search request with scrolling and a query:

.. code-block:: js

    curl -XGET 'localhost:9200/_search?search_type=scan&scroll=10m&size=50' -d '
    {
        "query" : {
            "match_all" : {}
        }
    }
    '


The **scroll** parameter control the keep alive time of the scrolling request and initiates the scrolling process. The timeout applies per round trip (i.e. between the previous scan scroll request, to the next).


The response will include no hits, with two important results, the **total_hits** will include the total hits that match the query, and the **scroll_id** that allows to start the scroll process. From this stage, the **_search/scroll** endpoint should be used to scroll the hits, feeding the next scroll request with the previous search result **scroll_id**. For example:


.. code-block:: js

    curl -XGET 'localhost:9200/_search/scroll?scroll=10m' -d 'c2NhbjsxOjBLMzdpWEtqU2IyZHlmVURPeFJOZnc7MzowSzM3aVhLalNiMmR5ZlVET3hSTmZ3OzU6MEszN2lYS2pTYjJkeWZVRE94Uk5mdzsyOjBLMzdpWEtqU2IyZHlmVURPeFJOZnc7NDowSzM3aVhLalNiMmR5ZlVET3hSTmZ3Ow=='


Scroll requests will include a number of hits equal to the size multiplied by the number of primary shards.


The "breaking" condition out of a scroll is when no hits has been returned. The total_hits will be maintained between scroll requests.


Note, scan search type does not support sorting (either on score or a field) or faceting.

