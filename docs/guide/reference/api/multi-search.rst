.. _es-guide-reference-api-multi-search:

============
Multi Search
============

The multi search API allows to execute several search requests within the same API. The endpoint for it is **_msearch** (available from **0.19** onwards). 


The format of the request is similar to the bulk API format, and the structure is as follows (the structure is specifically optimized to reduce parsing if a specific search ends up redirected to another node):


.. code-block:: js

    header\n
    body\n
    header\n
    body\n


The header part includes which index / indices to search on, optional (mapping) types to search on, the **search_type**, **preference**, and **routing**. The body includes the typical search body request (including the **query**, **facets**, **from**, **size**, and so on). Here is an example:


.. code-block:: js

    $ cat requests
    {"index" : "test"}
    {"query" : {"match_all" : {}}, "from" : 0, "size" : 10}
    {"index" : "test", "search_type" : "count"}
    {"query" : {"match_all" : {}}}
    {}
    {"query" : {"match_all" : {}}}
    
    {"query" : {"match_all" : {}}}
    {"search_type" : "count"}
    {"query" : {"match_all" : {}}}
    
    $ curl -XGET localhost:9200/_msearch --data-binary **requests; echo


Note, the above includes an example of an empty header (can also be just without any content) which is supported as well.


The response returns a **responses** array, which includes the search response for each search request matching its order in the original multi search request. If there was a complete failure for that specific search request, an object with **error** message will be returned in place of the actual search response.


The endpoint allows to also search against an index/indices and type/types in the URI itself, in which case it will be used as the default unless explicitly defined otherwise in the header. For example:


.. code-block:: js

    $ cat requests
    {}
    {"query" : {"match_all" : {}}, "from" : 0, "size" : 10}
    {}
    {"query" : {"match_all" : {}}}
    {"index" : "test2"}
    {"query" : {"match_all" : {}}}
    
    $ curl -XGET localhost:9200/test/_msearch --data-binary **requests; echo


The above will execute the search against the **test** index for all the requests that don't define an index, and the last one will be executed against the **test2** index.


