================
Has Child Filter
================

The **has_child** filter accepts a query and the child type to run against, and results in parent documents that have child docs matching the query. Here is an example:


.. code-block:: js


    {
        "has_child" : {
            "type" : "blog_tag"
            "query" : {
                "term" : {
                    "tag" : "something"
                }
            }
        }
    }    


The **type** is the child type to query against. The parent type to return is automatically detected based on the mappings.


The way that the filter is implemented is by first running the child query, doing the matching up to the parent doc for each document matched.


Scope
=====

A **_scope** can be defined on the filter allowing to run facets on the same scope name that will work against the child documents. For example:


.. code-block:: js


    {
        "has_child" : {
            "_scope" : "my_scope",
            "type" : "blog_tag"
            "query" : {
                "term" : {
                    "tag" : "something"
                }
            }
        }
    }    


Memory Considerations
=====================

With the current implementation, all **_id** values are loaded to memory (heap) in order to support fast lookups, so make sure there is enough mem for it.
