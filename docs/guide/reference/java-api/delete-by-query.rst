.. _es-guide-reference-java-api-delete-by-query:

===============
Delete By Query
===============

The delete by query API allows to delete documents from one or more indices and one or more types based on a query. The query can either be provided the :ref:`Query DSL <es-guide-reference-java-api-query-dsl>`.  Here is an example:



.. code-block:: java


    import static org.elasticsearch.index.query.FilterBuilders.*;
    import static org.elasticsearch.index.query.QueryBuilders.*;
    
    DeleteByQueryResponse response = client.prepareDeleteByQuery("test")
            .setQuery(termQuery("_type", "type1"))
            .execute()
            .actionGet();


For more information on the delete by query operation, check out the :ref:`delete_by_query API <es-guide-reference-java-api-delete-by-query>`  docs.

