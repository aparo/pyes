.. _es-guide-reference-api-index:
.. _es-guide-reference-api:

===
Api
===

This section describes the REST APIs *elasticsearch* provides (mainly) using JSON. The API is exposed using :ref:`HTTP <es-guide-reference-modules-http>`,  :ref:`thrift <es-guide-reference-modules-thrift>`,  :ref:`memcached <es-guide-reference-modules-memcached>`.  

Nodes
=====

Most cluster level APIs allow to specify which nodes to execute on (for example, getting the node stats for a node). Nodes can be identified in the APIs either using their internal node id, the node name, address, custom attributes, or just the **_local** node receiving the request. For example, here are some sample executions of nodes info:


.. code-block:: js

    # Local    
    curl localhost:9200/_cluster/nodes/_local
    # Address
    curl localhost:9200/_cluster/nodes/10.0.0.3,10.0.0.4
    curl localhost:9200/_cluster/nodes/10.0.0.*
    # Names
    curl localhost:9200/_cluster/nodes/node_name_goes_here
    curl localhost:9200/_cluster/nodes/node_name_goes_*
    # Attributes (set something like node.rack: 2 in the config)
    curl localhost:9200/_cluster/nodes/rack:2
    curl localhost:9200/_cluster/nodes/ra*:2
    curl localhost:9200/_cluster/nodes/ra*:2*


Options
=======

Pretty Results
--------------

When appending **?pretty=true** to any request made, the JSON returned will be pretty formatted (use it for debugging only!).


Parameters
----------

Rest parameters (when using HTTP, map to HTTP URL parameters) follow the convention of using underscore casing.


Boolean Values
--------------

All REST APIs parameters (both request parameters and JSON body) support providing boolean "false" as the values: **false**, **0** and **off**. All other values are considered "true". Note, this is not related to fields within a document indexed treated as boolean fields.


Number Values
-------------

All REST APIs support providing numbered parameters as **string** on top of supporting the native JSON number types.


Result Casing
-------------

All REST APIs accept the **case** parameter. When set to **camelCase**, all field names in the result will be returned in camel casing, otherwise, underscore casing will be used. Note, this does not apply to the source document indexed.


JSONP
-----

All REST APIs accept a **callback** parameter resulting in a `JSONP <http://en.wikipedia.org/wiki/JSONP>`_  result.

Request body in query string
----------------------------

For libraries that don't accept a request body for non-POST requests, you can pass the request body as the **source** query string parameter instead.

.. toctree::
    :maxdepth: 1

    admin-cluster-health
    admin-cluster-nodes-info
    admin-cluster-nodes-shutdown
    admin-cluster-nodes-stats
    admin-cluster-state
    admin-cluster-update-settings
    admin-indices-aliases
    admin-indices-analyze
    admin-indices-clearcache
    admin-indices-create-index
    admin-indices-delete-index
    admin-indices-delete-mapping
    admin-indices-flush
    admin-indices-gateway-snapshot
    admin-indices-get-mapping
    admin-indices-indices-exists
    admin-indices-open-close
    admin-indices-optimize
    admin-indices-put-mapping
    admin-indices-refresh
    admin-indices-segments
    admin-indices-stats
    admin-indices-status
    admin-indices-templates
    admin-indices-get-settings
    admin-indices-update-settings
    bulk
    count
    delete-by-query
    delete
    get
    index_
    more-like-this
    multi-get
    multi-index
    multi-search
    percolate
    search/index
    update
    validate
