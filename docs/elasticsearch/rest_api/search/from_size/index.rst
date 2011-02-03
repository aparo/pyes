From / Size
===========

Though can be set as request parameters, they can also be set within the search body. **from** defaults to **0**, and **size** defaults to **10**.


.. code-block:: js


    {
        "from" : 0, "size" : 10,
        "query" : {
            "term" : { "user" : "kimchy" }
        }
    }

