.. _es-guide-reference-query-dsl-exists-filter:

=============
Exists Filter
=============

Filters documents where a specific field has a value in them.


.. code-block:: js


    {
        "constant_score" : {
            "filter" : {
                "exists" : { "field" : "user" }
            }
        }
    }


Caching
=======

The result of the filter is always cached.

