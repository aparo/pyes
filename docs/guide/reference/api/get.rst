.. _es-guide-reference-api-get:

===
Get
===

The get API allows to get a typed JSON document from the index based on its id. The following example gets a JSON document from an index called twitter, under a type called tweet, with id valued 1:


.. code-block:: js

    curl -XGET 'http://localhost:9200/twitter/tweet/1'


The result of the above get operation is:


.. code-block:: js


    {
        "_index" : "twitter",
        "_type" : "tweet",
        "_id" : "1", 
        "_source" : {
            "user" : "kimchy",
            "postDate" : "2009-11-15T14:12:12",
            "message" : "trying out Elastic Search"
        }
    }


The above result includes the **_index**, **_type**, and **_id** of the document we wish to retrieve, including the actual source of the document that was indexed.


The API also allows to check for the existance of a document using **HEAD**, for example:


.. code-block:: js

    curl -XHEAD 'http://localhost:9200/twitter/tweet/1'


Realtime
========

By default, the get API is realtime, and is not affected by the refresh rate of the index (when data will become visible for search).


In order to disable realtime GET, one can either set **realtime** parameter to **false**, or globally default it to by setting the **action.get.realtime** to **false** in the node configuration.


When getting a document, one can specify **fields** to fetch from it. They will, when possible, be fetched as stored fields (fields mapped as stored in the mapping). When using realtime GET, there is no notion of stored fields (at least for a period of time, basically, until the next flush), so they will be extracted from the source itself (note, even if source is not enabled). It is a good practice to assume that the fields will be loaded from source when using realtime GET, even if the fields are stored.


Optional Type
=============

The get API allows for **_type** to be optional. Set it to **_all** in order to fetch the first document matching the id across all types.


Fields
======

The get operation allows to specify a set of fields that will be returned (by default, its the **_source** field) by passing the **fields** parameter. For example:


.. code-block:: js

    curl -XGET 'http://localhost:9200/twitter/tweet/1?fields=title,content'


The returned fields will either be loaded if they are stored, or fetched from the **_source** (parsed and extracted). It also supports sub objects extraction from _source, like **obj1.obj2**.


Routing
=======

When indexing using the ability to control the routing, in order to get a document, the routing value should also be provided. For example:


.. code-block:: js

    curl -XGET 'http://localhost:9200/twitter/tweet/1?routing=kimchy'


The above will get a tweet with id 1, but will be routed based on the user. Note, issuing a get without the correct routing, will cause the document not to be fetched.


Preference
==========

Controls a **preference** of which shard replicas to execute the get request on. By default, the operation is randomized between the each shard replicas.


The **preference** can be set to:

* **_primary**: The operation will go and be executed only on the primary shards.
* **_local**: The operation will prefer to be executed on a local allocated shard is possible.
* Custom (string) value: A custom value will be used to guarantee that the same shards will be used for the same custom value. This can help with "jumping values" when hitting different shards in different refresh states. A sample value can be something like the web session id, or the user name.

Refresh
=======

The **refresh** parameter can be set to **true** in order to refresh the relevant shard before the get operation and make it searchable. Setting it to **true** should be done after careful thought and verification that this does not cause a heavy load on the system (and slows down indexing).


Distributed
===========

The get operation gets hashed into a specific shard id. It then gets redirected to one of the replicas within that shard id and returns the result. The replicas are the primary shard and its replicas within that shard id group. This means that the more replicas we will have, the better GET scaling we will have.
