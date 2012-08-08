.. _es-guide-reference-api-search-version:

=======
Version
=======

Returns a version for each search hit.


.. code-block:: js


    {
        "version": true,
        "query" : {
            "term" : { "user" : "kimchy" }
        }
    }

