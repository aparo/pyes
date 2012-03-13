.. _es-guide-reference-api-admin-indices-clearcache:

========================
Admin Indices Clearcache
========================

The clear cache API allows to clear either all caches or specific cached associated with one ore more indices.


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/twitter/_cache/clear'


The API, by default, will clear all cached. Specific caches can cleaned explicitly by setting **filter**, **field_data** or **bloom** to **true**.


All caches relating to a specific field(s) can also be cleared by specifying **fields** parameter with a comma delimited list of the relevant fields.


Multi Index
===========

The flush API can be applied to more than one index with a single call, or even on **_all** the indices.


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/kimchy,elasticsearch/_cache/clear'
    
    $ curl -XPOST 'http://localhost:9200/_cache/clear'

