.. _es-guide-reference-java-api-search:

======
Search
======

The search API allows to execute a search query and get back search hits that match the query. It can be executed across one or more indices and across one or more types. The query can either be provided using the :ref:`Query DSL <es-guide-reference-java-api-query-dsl>`.  ference-java-api-query-dsl>`.  The body of the search request is built using the **SearchSourceBuilder**. Here is an example:

.. code-block:: java


    import static org.elasticsearch.index.query.xcontent.FilterBuilders.*;
    import static org.elasticsearch.index.query.xcontent.QueryBuilders.*;
    
    SearchResponse response = client.prepareSearch("test")
            .setSearchType(SearchType.DFS_QUERY_THEN_FETCH)
            .setQuery(termQuery("multi", "test"))
            .setFrom(0).setSize(60).setExplain(true))
            .execute()
            .actionGet();


For more information on the search operation, check out the REST :ref:`search <es-guide-reference-java-api-search>`  docs.


Operation Threading
===================

The search API allows to set the threading model the operation will be performed when the actual execution of the API is performed on the same node (the API is executed on a shard that is allocated on the same server).


There are three threading modes.The **NO_THREADS** mode means that the search operation will be executed on the calling thread. The **SINGLE_THREAD** mode means that the search operation will be executed on a single different thread for all local shards. The **THREAD_PER_SHARD** mode means that the search operation will be executed on a different thread for each local shard.


The default mode is **SINGLE_THREAD**.

