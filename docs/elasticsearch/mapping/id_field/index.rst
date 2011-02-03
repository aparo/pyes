Id Field
========

Each document indexed is associated with an id and a type. The id, when indexing, is automatically indexed into an **_id** field. By default, the **_id** field is indexed (but *not* analyzed) and not stored. This means that the **_id** field can be used to query against it.


The **_id** field allows to store it as well, for example:


.. code-block:: js


    {
        "tweet" : {
            "_id" : {"store" : "yes"}
        }
    }

