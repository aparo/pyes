REST API
========

This section describes the REST APIs ElasticSearch provides using JSON. The following are the main APIs one would need in order to get started with ElasticSearch:


===========================================================  =======================================================================================
 API                                                          Description                                                                           
===========================================================  =======================================================================================
:doc:`index <./index/index>`                                 Index a typed JSON document into a specific index and make it searchable.              
:doc:`delete <./delete/index>`                               Delete a typed JSON document from a specific index based on its id.                    
:doc:`bulk <./bulk/index>`                                   Index and delete json several documents in a single request.                           
:doc:`get <./get/index>`                                     Get a typed JSON document from an index based on its id.                               
:doc:`search <./search/index>`                               Execute a search query against one or more indices and get back search hits.           
:doc:`count <./count/index>`                                 Execute a query against one or more indices and get hits count.                        
:doc:`create_index <./admin/indices/create_index/index>`     Creates an index with optional settings.                                               
:doc:`delete_index <./admin/indices/delete_index/index>`     Deletes an index.                                                                      
:doc:`put_mapping <./admin/indices/put_mapping/index>`       Register specific mapping definition for a specific type against one or more indices.  
===========================================================  =======================================================================================

There is also an evolving :doc:`Administration REST API <./admin/index>`. 

Exported REST Layers
--------------------

The REST API is exposed using :doc:`HTTP </elasticsearch/modules/http/index>`, :doc:`Memcached </elasticsearch/modules/memcached/index>`. 

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

All REST APIs accept a **callback** parameter resulting in a `JSONP <http://en.wikipedia.org/wiki/JSON#JSONP>` result.

