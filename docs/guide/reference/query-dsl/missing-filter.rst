==============
Missing Filter
==============

Filters documents where a specific field has no value in them.


.. code-block:: js


    {
        "constant_score" : {
            "filter" : {
                "missing" : { "field" : "user" }
            }
        }
    }


Caching
=======

The result of the filter is always cached.

