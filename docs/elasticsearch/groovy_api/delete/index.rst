Delete
======

The delete API is very similar to the :doc:`Java delete API </elasticsearch/java_api/delete/index>`, here is an example:


.. code-block:: js

    def deleteF = node.client.delete {
        index "test"
        type "type1"
        id "1"
    }

