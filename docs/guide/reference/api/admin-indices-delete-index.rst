.. _es-guide-reference-api-admin-indices-delete-index:
.. _es-guide-reference-api-admin-indices-delete:

==========================
Admin Indices Delete Index
==========================

The delete index API allows to delete an existing index.


.. code-block:: js

    $ curl -XDELETE 'http://localhost:9200/twitter/'


The above example deletes an index called **twitter**.


The delete index API can also be applied to more than one index, or on **_all** indices (be careful!). All indices will also be deleted when no specific index is provided. In order to disable allowing to delete all indices, set **action.disable_delete_all_indices** setting in the config to **true**.

