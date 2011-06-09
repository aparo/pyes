.. _es-guide-reference-mapping-size-field:

==========
Size Field
==========

The **_size** field allows to automatically index the size of the original **_source** indexed (not the compressed size, if compressed). By default, its disabled. In order to enable it, set the mapping to:


.. code-block:: js


    {
        "tweet" : {
            "_size" : {"enabled" : true}
        }
    }


In order to also store it, use:


.. code-block:: js


    {
        "tweet" : {
            "_size" : {"enabled" : true, "store" : "yes"}
        }
    }

