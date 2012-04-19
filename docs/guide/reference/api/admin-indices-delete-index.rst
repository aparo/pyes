.. _es-guide-reference-api-admin-indices-delete-index:

==========================
Admin Indices Delete Index
==========================

The delete index API allows to delete an existing index.


.. code-block:: js

    $ curl -XDELETE 'http://localhost:9200/twitter/'


The above example deletes an index called **twitter**.


The delete index API can also be applied to more than one index, or on **_all** indices (be careful!). All indices will also be deleted when no specific index is provided.

