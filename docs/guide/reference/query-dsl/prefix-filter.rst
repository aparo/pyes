=============
Prefix Filter
=============

Filters documents that have fields containing terms with a specified prefix. Similar to phrase query, except that it acts as a filter. Can be placed within queries that accept a filter.


.. code-block:: js


    {
        "constant_score" : {
            "filter" : {
                "prefix" : { "user" : "ki" }
            }
        }
    }


Caching
=======

The result of the filter is cached by default. The `_cache` can be set to `false` in order not to cache it.

