.. _es-guide-reference-java-api-query-dsl:

=========
Query Dsl
=========

elasticsearch provides a full Java query dsl in a similar manner to the REST :ref:`Query DSL <es-guide-reference-query-dsl>`.  The factory for query builders is **QueryBuilders** and the factory for filter builders is **FilterBuilders**. Here is an example:


.. code-block:: java


    import static org.elasticsearch.index.query.FilterBuilders.*;
    import static org.elasticsearch.index.query.QueryBuilders.*;
    
    QueryBuilder qb1 = termQuery("name", "kimchy");
    
    QueryBuilder qb2 = boolQuery()
                        .must(termQuery("content", "test1"))
                        .must(termQuery("content", "test4"))
                        .mustNot(termQuery("content", "test2"))
                        .should(termQuery("content", "test3"));
    
    QueryBuilder qb3 = filteredQuery(
                termQuery("name.first", "shay"), 
                rangeFilter("age")
                    .from(23)
                    .to(54)
                    .includeLower(true)
                    .includeUpper(false)
                );


The **QueryBuilder** can then be used with any API that accepts a query, such as **count** and **search**.

