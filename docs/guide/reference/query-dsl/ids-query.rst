.. _es-guide-reference-query-dsl-ids-query:

=========
Ids Query
=========

Filters documents that only have the provided ids. Note, this filter does not require the **_id** field to be indexed since it works using the **_uid** field.


.. code-block:: js


    {
        "ids" : {
            "type" : "my_type",
            "values" : ["1", "4", "100"]
        }
    }    


The **type** is optional and can be omitted, and can also accept an array of values.

