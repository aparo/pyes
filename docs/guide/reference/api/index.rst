.. _es-guide-reference-api-index:

===
Api
===

This section describes the REST APIs *elasticsearch* provides (mainly) using JSON. The API is exposed using :ref:`HTTP <es-guide-reference-modules-http>`,  :ref:`thrift <es-guide-reference-modules-thrift>`,  :ref:`memcached <es-guide-reference-modules-memcached>`.  

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

You can also use the **source** query string parameter to substitute for the body of the request.



.. toctree::
    :maxdepth: 1

    admin-cluster-health
    admin-cluster-nodes-info
    admin-cluster-nodes-shutdown
    admin-cluster-nodes-stats
    admin-cluster-state
    admin-indices-aliases
    admin-indices-analyze
    admin-indices-clearcache
    admin-indices-create-index
    admin-indices-delete-index
    admin-indices-delete-mapping
    admin-indices-flush
    admin-indices-gateway-snapshot
    admin-indices-get-mapping
    admin-indices-open-close
    admin-indices-optimize
    admin-indices-put-mapping
    admin-indices-refresh
    admin-indices-status
    admin-indices-templates
    admin-indices-update-settings
    bulk
    count
    delete-by-query
    delete
    get
    index_
    more-like-this
    percolate
    search/index