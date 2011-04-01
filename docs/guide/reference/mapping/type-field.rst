.. _es-guide-reference-mapping-type-field:

==========
Type Field
==========

Each document indexed is associated with an id and a type. The type, when indexing, is automatically indexed into a **_type** field. By default, the **_type** field is indexed (but *not* analyzed) and not stored. This means that the **_type** field can be queried.


The **_type** field can be stored as well, for example:


.. code-block:: js


    {
        "tweet" : {
            "_type" : {"store" : "yes"}
        }
    }

