.. _es-guide-reference-api-search-min-score:

=========
Min Score
=========

Allows to filter out documents based on a minimum score:


.. code-block:: js


    {
        "min_score": 0.5,
        "query" : {
            "term" : { "user" : "kimchy" }
        }
    }


Note, most times, this does not make much sense, but is provided for advance use cases.


