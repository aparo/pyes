.. _es-guide-reference-groovy-api-search:

======
Search
======

The search API is very similar to the :ref:`Java search API <es-guide-reference-java-api-search>`.  The Groovy extension allows to provide the search source to execute as a **Closure** including the query itself (similar to GORM criteria builder):


.. code-block:: js

    def search = node.client.search {
        indices "test"
        types "type1"
        source {
            query {
                term(test: "value")
            }
        }
    }

    search.response.hits.each {SearchHit hit ->
        println "Got hit $hit.id from $hit.index/$hit.type"
    }


It can also be execute using the "Java API" while still using a closure for the query:


.. code-block:: js

    def search = node.client.prepareSearch("test").setQuery({
            term(test: "value")
    }).gexecute();

    search.response.hits.each {SearchHit hit ->
        println "Got hit $hit.id from $hit.index/$hit.type"
    }


The format of the search **Closure** follows the same JSON syntax as the :ref:`Search API <es-guide-reference-groovy-api-search>`  request.


