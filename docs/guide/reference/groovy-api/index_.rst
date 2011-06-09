.. _es-guide-reference-groovy-api-index_:

======
Index_
======

The index API is very similar to the :ref:`Java index API <es-guide-reference-java-api-index_>`.  The Groovy extension to it is the ability to provide the indexed source using a closure. For example:


.. code-block:: js

    def indexR = client.index {
        index "test"
        type "type1"
        id "1"
        source {
            test = "value"
            complex {
                value1 = "value1"
                value2 = "value2"
            }
        }
    }


In the above example, the source closure itself gets transformed into an XContent (defaults to JSON). In order to change how the source closure is serialized, a global (static) setting can be set on the **GClient** by changing the **indexContentType** field.


Note also that the **source** can be set using the typical Java based APIs, the **Closure** option is a Groovy extension.

