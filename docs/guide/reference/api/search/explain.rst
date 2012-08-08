.. _es-guide-reference-api-search-explain:

=======
Explain
=======

Enables explanation for each hit on how its score was computed.


.. code-block:: js


    {
        "explain": true,
        "query" : {
            "term" : { "user" : "kimchy" }
        }
    }

