.. _es-guide-reference-api-get:

===
Get
===

The get API allows to get a typed JSON document from the index based on its id. The following example gets a JSON document from an index called twitter, under a type called tweet, with id valued 1:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/twitter/tweet/1'


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


Fields
======

The get operation allows to specify a set of fields that will be returned (by default, its the **_source** field) by passing the **fields** parameter. For example:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/twitter/tweet/1?fields=title,content'


Note
    The fields specified must be stored in order to retrieve them.


Routing
=======

When indexing using the ability to control the routing, in order to get a document, the routing value should also be provided. For example:


.. code-block:: js

    $ curl -XGET 'http://localhost:9200/twitter/tweet/1?routing=kimchy'


The above will get a tweet with id 1, but will be routed based on the user. Note, issuing a get without the correct routing, will cause the document not to be fetched.


Refresh
=======

The **refresh** parameter can be set to **true** in order to refresh the relevant shard before the get operation and make it searchable. Setting it to **true** should be done after careful thought and verification that this does not cause a heavy load on the system (and slows down indexing).


Distributed
===========

The get operation gets hashed into a specific shard id. It then gets redirected to one of the replicas within that shard id and returns the result. The replicas are the primary shard and its replicas within that shard id group. This means that the more replicas we will have, the better GET scaling we will have.
