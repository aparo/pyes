Fuzzy Query
===========

A fuzzy based query that uses similarity based on Levenshtein (edit distance) algorithm.


Note
    Warning: this query is not very scalable with its default prefix length of 0 - in this case, *every* term will be enumerated and cause an edit score calculation. Here is a simple example:


.. code-block:: js


    {
        "fuzzy" : { "user" : "ki" }
    }


More complex settings can be set (the values here are the default values):


.. code-block:: js


        {
            "fuzzy" : { 
                "user" : {
                    "value" : "ki",
                    "boost" : 1.0,
                    "min_similarity" : 0.5,
                    "prefix_length" : 0
                }
            }
        }

