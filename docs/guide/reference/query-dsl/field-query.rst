.. _es-guide-reference-query-dsl-field-query:

===========
Field Query
===========

A query that executes a query string against a specific field. It is a simplified version of :ref:`query_string <es-guide-reference-query-dsl-query-string-query>`  query (by setting the **default_field** to the field this query executed against). In its simplest form:


.. code-block:: js


    {
        "field" : { 
            "name.first" : "+something -else"
        }
    }


Most of the **query_string** parameters are allowed with the **field** query as well, in such a case, the query should be formatted as follows:


.. code-block:: js


    {
        "field" : { 
            "name.first" : {
                "query" : "+something -else",
                "boost" : 2.0,
                "enable_position_increments": false
            }
        }
    }

