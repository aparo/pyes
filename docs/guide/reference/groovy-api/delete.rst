.. _es-guide-reference-groovy-api-delete:

======
Delete
======

The delete API is very similar to the :ref:`Java delete API <es-guide-reference-groovy-java-api-delete>`,  here is an example:


.. code-block:: js

    def deleteF = node.client.delete {
        index "test"
        type "type1"
        id "1"
    }

