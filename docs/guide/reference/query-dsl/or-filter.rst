.. _es-guide-reference-query-dsl-or-filter:

=========
Or Filter
=========

A filter that matches documents using **OR** boolean operator on other queries. This filter is more performant then :ref:`bool <es-guide-reference-query-dsl-bool-filter>`  filter. Can be placed within queries that accept a filter.


.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "term" : { "name.first" : "shay" }
            },
            "filter" : {
                "or" : [
                    {
                        "term" : { "name.second" : "banon" }
                    },
                    {
                        "term" : { "name.nick" : "kimchy" }
                    }
                ]
            }
        }
    }


Caching
=======

The result of the filter is not cached by default. The **_cache** can be set to **true** in order to cache it (tough usually not needed). Since the **_cache** element requires to be set on the **or** filter itself, the structure then changes a bit to have the filters provided within a **filters** element:


.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "term" : { "name.first" : "shay" }
            },
            "filter" : {
                "or" : {
                    "filters" : [
                        {
                            "term" : { "name.second" : "banon" }
                        },
                        {
                            "term" : { "name.nick" : "kimchy" }
                        }
                    ],
                    "_cache" : true
                }
            }
        }
    }


