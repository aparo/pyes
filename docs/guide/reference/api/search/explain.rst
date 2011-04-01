.. _es-guide-reference-api-search-explain:

=======
Explain
=======

Enables explanation for each hit on how its score was computed.


.. code-block:: js


    {
        :ref:`explain <es-guide-reference-api-search>`  in <es-guide-reference-api-search>`  true,
        "query" : {
            "term" : { "user" : "kimchy" }
        }
    }

