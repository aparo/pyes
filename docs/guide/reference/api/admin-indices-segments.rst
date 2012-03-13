.. _es-guide-reference-api-admin-indices-segments:

======================
Admin Indices Segments
======================

Provide low level segments information that a Lucene index (shard level) is built with. Allows to be used to provide more information on the state of a shard and an index, possibly optimization information, data "wasted" on deletes, and so on.


Endpoints include segments for a specific index, several indices, or all:


.. code-block:: js

    curl -XGET 'http://localhost:9200/test/_segments'
    curl -XGET 'http://localhost:9200/test1,test2/_segments'
    curl -XGET 'http://localhost:9200/_segments'

