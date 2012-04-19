.. _es-guide-reference-api-search-facets-index:
.. _es-guide-reference-api-search-facets:

======
Facets
======

The usual purpose of a full-text search engine is to return a small number of documents matching your query.

_Facets_ provide aggregated data based on a search query. In the simple case, a facet can return **facet counts** for various **facet values** for a specific **field**. ElasticSearch supports more advanced facet implementations, such as :ref:`statistical <es-guide-reference-api-search-facets-statistical-facet>`  api:ref:`date histogram <es-guide-reference-api-search-facets-date-histogram-facet>`  earch/facets/date-histogram-facet.html facets.

The field used for facet calculations must be of type numeric, date/time or analyzed as a single token. You can give the facet an arbitrary _name_ and return multiple facets in one request.

For example, let's suppose you have a number of articles with a field called **tags**. Facet can return counts for the most popular tags across the documents matching your query — or across all documents in the index.

Let's check out this simple example. We will store some example data first:

.. code-block:: js


    curl -X DELETE "http://localhost:9200/articles"
    curl -X POST "http://localhost:9200/articles/article" -d '{"title" : "One",   "tags" : ["foo"]}'
    curl -X POST "http://localhost:9200/articles/article" -d '{"title" : "Two",   "tags" : ["foo", "bar"]}'
    curl -X POST "http://localhost:9200/articles/article" -d '{"title" : "Three", "tags" : ["foo", "bar", "baz"]}'


Now, let's query the index for articles beginning with letter “T” and retrieve a :ref:`terms facet <es-guide-reference-api-search-facets-terms-facet>`  for the **tags** field:

.. code-block:: bash


    curl -X POST "http://localhost:9200/articles/_search?pretty=true" -d '
      {
        "query" : { "query_string" : {"query" : "T*"} },
        "facets" : {
          "tags" : { "terms" : {"field" : "tags"} }
        }
      }
    '


This request will return articles “Two” and “Three”, as well as the **tags** facet:

.. code-block:: js


    "facets" : {
      "tags" : {
        "_type" : "terms",
        "missing" : 0,
        "terms" : [ {
          "term" : "foo",
          "count" : 2
        }, {
          "term" : "bar",
          "count" : 2
        }, {
          "term" : "baz",
          "count" : 1
        } ]
      }
    }


Notice that the counts are scoped for this query: _foo_ and _bar_ are counted twice, _baz_ is counted once. (This is because the primary purpose of facets is to enable `_faceted browsing_ <http://en.wikipedia.org/wiki/Faceted_search>`_,  _,  allowing the user to refine her query based on the insight from the facet: restrict the search to a specific category, price or date range, etc., most probably wit:ref:`_filter_ <es-guide-reference-api-search-filter>`  tml based on selected facet.)

Scope
-----

Facets are bound to the current query by default, called **main**. Every facet can be set with the **global** scope, in which case it will return facet calculations for all documents in the index.

A shorthand to set a facet to run globally is to set the **global** parameter to **true**:

.. code-block:: js


    {
        "facets" : {
            "<FACET NAME>" : {
                "<FACET TYPE>" : { ... },
                "global" : true
            }
        }
    }    


Custom scope names works in conjunction with child queries or filters, allowing to force the facets to run on the child documents matching the child specific query.

Filter
------

All facets can be configured with an additional filter (explained in the :ref:`Query DSL <es-guide-reference-query-dsl>`  -search-facets-guide-reference-query-dsl>`  section), which will further reduce the documents they execute on. For example:

.. code-block:: js


    {
        "facets" : {
            "<FACET NAME>" : {
                "<FACET TYPE>" : {
                    ...
                },
                "facet_filter" : {
                    "term" : { "user" : "kimchy"}
                }
            }
        }
    }    


.. toctree::
    :maxdepth: 1

    date-histogram-facet
    filter-facet
    geo-distance-facet
    histogram-facet
    query-facet
    range-facet
    statistical-facet
    terms-facet
    terms-stats-facet
