.. _es-guide-reference-mapping-multi-field-type:

================
Multi Field Type
================

The **multi_field** type allows to map several :ref:`core_types <es-guide-reference-mapping-core-types>`  of the same value. This can come very handy, for example, when wanting to map a **string** type, once when its **analyzed** and once when its **not_analyzed**. For example:


.. code-block:: js


    {
        "tweet" : {
            "properties" : {
                "name" : {
                    "type" : "multi_field",
                    "fields" : {
                        "name" : {"type" : "string", "index" : "analyzed"},
                        "untouched" : {"type" : "string", "index" : "not_analyzed"}
                    }
                }
            }
        }
    }


The above example shows how the **name** field, which is of simple **string** type, gets mapped twice, once with it being **analyzed** under **name**, and once with it being **not_analyzed** under **untouched**.


Accessing Fields
================

With **multi_field** mapping, the field that has the same name as the property is treated as if it was mapped without a multi field. Thats the "default" field. It can be accessed regularly, for example using **name** or using typed navigation **tweet.name**. 


Other fields with different names can be easily accessed using the navigation notation, for example, using: **name.untouched**, or using the typed navigation notation **tweet.name.untouched**.


Merging
=======

When updating mapping definition using the **put_mapping** API, a core type mapping can be "upgraded" to a **multi_field** mapping. This means that if the old mapping has a plain core type mapping, the updated mapping for the same property can be a **multi_field** type, with the default field being the one being replaced.

