Type Field
==========

Each document indexed is associated with an id and a type. The type, when indexing, is automatically indexed into an **_type** field. By default, the **_type** field is indexed (but *not* analyzed) and not stored. This means that the **_type** field can be used to query against it.


The **_type** field allows to store it as well, for example:


.. code-block:: js


    {
        "tweet" : {
            "_type" : {"store" : "yes"}
        }
    }

