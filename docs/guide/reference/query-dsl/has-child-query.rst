.. _es-guide-reference-query-dsl-has-child-query:

===============
Has Child Query
===============

The **has_child** query works the same as the :ref:`has_child <es-guide-reference-query-dsl-has-child-filter>`  filter, by automatically wrapping the filter with a :ref:`constant_score <es-guide-reference-query-dsl-constant-score-query>`.  It has the same syntax as the :ref:`has_child <es-guide-reference-query-dsl-has-child-filter>`  filter:


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


Scope
-----

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
