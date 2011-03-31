===============
Delete By Query
===============

The delete by query API allows to delete documents from one or more indices and one or more types based on a query. The query can either be provided the :doc:`Query DSL <.//query_dsl>`.  Here is an example:



.. code-block:: java


    import static org.elasticsearch.index.query.xcontent.FilterBuilders.*;
    import static org.elasticsearch.index.query.xcontent.QueryBuilders.*;
    
    DeleteByQueryResponse response = client.prepareDeleteByQuery("test")
            .setQuery(termQuery("_type", "type1"))
            .execute()
            .actionGet();


For more information on the delete by query operation, check out the :doc:`delete_by_query API <.//guide/reference/api/delete-by-query.html>`  docs.

