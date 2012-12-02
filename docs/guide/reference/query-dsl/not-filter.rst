.. _es-guide-reference-query-dsl-not-filter:

==========
Not Filter
==========

A filter that filters out matched documents using a query. This filter is more performant then :ref:`bool <es-guide-reference-query-dsl-bool-filter>`  filter. Can be placed within queries that accept a filter.


.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "term" : { "name.first" : "shay" }
            },
            "filter" : {
                "not" : {
                    "range" : {
                        "postDate" : {
                            "from" : "2010-03-01",
                            "to" : "2010-04-01"
                        }
                    }
                }
            }
        }
    }


Or, in a longer form with a **filter** element:


.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "term" : { "name.first" : "shay" }
            },
            "filter" : {
                "not" : {
                    "filter" :  {
                        "range" : {
                            "postDate" : {
                                "from" : "2010-03-01",
                                "to" : "2010-04-01"
                            }
                        }
                    }
                }
            }
        }
    }



Caching
=======

The result of the filter is not cached by default. The **_cache** can be set to **true** in order to cache it (tough usually not needed). Here is an example:


.. code-block:: js


    {
        "filtered" : {
            "query" : {
                "term" : { "name.first" : "shay" }
            },
            "filter" : {
                "not" : {
                    "filter" :  {
                        "range" : {
                            "postDate" : {
                                "from" : "2010-03-01",
                                "to" : "2010-04-01"
                            }
                        }
                    },
                    "_cache" : true
                }
            }
        }
    }

