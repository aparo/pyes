.. _es-guide-reference-mapping-nested-type:

===========
Nested Type
===========

Nested objects/documents allow to map certain sections in the document indexed as nested allowing to query them as if they are separate docs joining with the parent owning doc.


Note
    This feature is experimental and might require reindexing the data if using it.


One of the problems when indexing inner objects that occur several times in a doc is that "cross object" search match will occur, for example:


.. code-block:: js


    {
        "obj1" : [
            {
                "name" : "blue",
                "count" : 4
            },
            {
                "name" : "green",
                "count" : 6
            }
        ]
    }


Searching for name set to blue and count higher than 5 will match the doc, because in the first element the name matches blue, and in the second element, count matches "higher than 5".


Nested mapping allow to map certain inner objects (usually multi instance ones), for example:


.. code-block:: js


    {
        "type1" : {
            "properties" : {
                "obj1" : {
                    "type" : "nested"
                }
            }
        }
    }


The above will cause all **obj1** to be indexed as a nested doc. The mapping is similar in nature to setting **type** to **object**, except that its **nested**.


The **nested** object fields can also be automatically added to the immediate parent by setting **include_in_parent** to true, and also included in the root object by setting **include_in_root** to true.


Nested docs will also automatically use the root doc **_all** field.


Searching on nested docs can be done using either the :ref:`nested query <es-guide-reference-query-dsl-nested-query>`  or :ref:`nested filter <es-guide-reference-query-dsl-nested-filter>`.  

Internal Implementation
-----------------------

Internally, nested objects are indexed as additional documents, but, since they can be guaranteed to be indexed within the same "block", it allows for extremely fast joining with parent docs.


Those internal nested documents are automatically masked away when doing operations against the index (like searching with a match_all query), and they bubble out when using the nested query.
