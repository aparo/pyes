.. _es-guide-reference-api-admin-indices-flush:

===================
Admin Indices Flush
===================

The flush API allows to flush one or more indices through an API. The flush process of an index basically frees memory from the index by flushing data to the index storage and clearing the internal transaction log. By default, ElasticSearch uses memory heuristics in order to automatically trigger flush operations as required in order to clear memory.


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/twitter/_flush'


Request Parameters
==================

The flush API accepts the following request parameters:


===============  =========================================================================
 Name             Description                                                             
===============  =========================================================================
 **refresh**      Should a refresh be performed after the flush. Defaults to **false**.   
===============  =========================================================================

Multi Index
===========

The flush API can be applied to more than one index with a single call, or even on **_all** the indices.


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/kimchy,elasticsearch/_flush'
    
    $ curl -XPOST 'http://localhost:9200/_flush'

