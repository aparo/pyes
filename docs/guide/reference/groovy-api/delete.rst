======
Delete
======

The delete API is very similar to the :doc:`Java delete API <.//guide/reference/java-api/delete.html>`,  here is an example:


.. code-block:: js

    def deleteF = node.client.delete {
        index "test"
        type "type1"
        id "1"
    }

