.. _es-guide-reference-query-dsl-type-filter:

===========
Type Filter
===========

Filters documents matching the provided document / mapping type. Note, this filter can work even when the **_type** field is not indexed (using the **_uid** field).



.. code-block:: js


    {
        "type" : {
            "value" : "my_type"
        }
    }    

