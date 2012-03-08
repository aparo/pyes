.. _es-guide-reference-mapping-boost-field:

===========
Boost Field
===========

Boosting is the process of enhancing the relevancy of a document or field. Field level mapping allows to define explicit boost level on a specific field. The boost field mapping (applied on the :ref:`root object <es-guide-reference-mapping-root-object-type>`  allows to define a boost field mapping where *its content will control the boost level of the document*. For example, consider the following mapping:


.. code-block:: js


    {
        "tweet" : {
            "_boost" : {"name" : "_boost", "null_value" : 1.0}
        }
    }


The above mapping defines mapping for a field named **_boost**. If the **_boost** field exists within the JSON document indexed, its value will control the boost level of the document indexed. For example, the following JSON document will be indexed with a boost value of **2.2**:


.. code-block:: js


    {
        "tweet" {
            "_boost" : 2.2,
            "message" : "This is a tweet!"
        }
    }


