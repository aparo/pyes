.. _es-guide-reference-query-dsl-custom-boost-factor-query:

=========================
Custom Boost Factor Query
=========================

**custom_boost_factor** query allows to wrap another query and multiply its score by the provided **boost_factor**. This can sometimes be desired since **boost** value set on specific queries gets normalized, while this query boost factor does not.


.. code-block:: js


    "custom_boost_factor" : {
        "query" : {
            ....
        },
        "boost_factor" : 5.2
    }

