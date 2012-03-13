.. _es-guide-reference-api-admin-indices-indices-exists:

============================
Admin Indices Indices Exists
============================

Used to check if the index (indices) exists or not. For example:


.. code-block:: js

    curl -XHEAD 'http://localhost:9200/twitter'


The HTTP status code indicates if it exists or not. A **404** means its not found, and **200** means its there.

