.. _es-guide-reference-query-dsl-match-all-filter:

================
Match All Filter
================

A filter that matches on all documents:


.. code-block:: js


    {
        "constant_score" : {
            "filter" : {
                "match_all" : { }
            }
        }
    }

