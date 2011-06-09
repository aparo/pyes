.. _es-guide-reference-api-index_:

======
Index_
======

The index API allows to index a typed JSON document into a specific index and make it searchable. The following example index the JSON document into an index called twitter, under a type called tweet, with id valued 1:


.. code-block:: js

    $ curl -XPUT 'http://localhost:9200/twitter/tweet/1' -d '{
        "user" : "kimchy",
        "post_date" : "2009-11-15T14:12:12",
        "message" : "trying out Elastic Search"
    }'


The result of the above index operation is:


.. code-block:: js


    {
        "ok" : true,
        "_index" : "twitter",
        "_type" : "tweet",
        "_id" : "1"
    }


Automatic for the Index
=======================

The index operation automatically creates an index if it has not been created before (check out the :ref:`create index API <es-guide-reference-api-admin-indices-create-index>`  for manually creating an index), and also automatically creates a dynamic type mapping for the specific type if it has not been created before (check out the :ref:`put mapping <es-guide-reference-api-admin-indices-put-mapping>`  API for manually creating type mapping). 


The mapping itself is very flexible and is schema free, meaning that new fields / objects can be added and they will automatically be added to the mapping definition of the specific type. Check out the :ref:`mapping <es-guide-reference-mapping>`  section for more information on mapping definitions.


Though explained on the :ref:`mapping <es-guide-reference-mapping>`  section, its important to note that the format of the JSON document can also include the type (very handy when using JSON mappers), for example:


.. code-block:: js

    $ curl -XPUT 'http://localhost:9200/twitter/tweet/1' -d '{
        "tweet" : {
            "user" : "kimchy",
            "post_date" : "2009-11-15T14:12:12",
            "message" : "trying out Elastic Search"
        }
    }'


Versioning
==========

Each document indexed is versioned. When indexing a doc, the **version** that is associated with it is returned as part of the response. The index API allows for `optimistic concurrency control <http://en.wikipedia.org/wiki/Optimistic_concurrency_control>`_  by allowing to specify the version the index should be updated under. This is handy for example when doing read and update, and making sure no changes happened in the meantime (when reading, make sure to set the **preference** to **_primary**). For example:


.. code-block:: js

    curl -XPUT 'localhost:9200/twitter/tweet/1?version=2' -d '{
        "message" : "elasticsearch now has versioning support, double cool!"
    }'


Note, versioning are completely real time, and are not affect by the near real time aspect of get and search operations. If no version is provided, then the operation is forced to be executed without any checks.


By default, an internal versioning systems will be used, but, the versioning can be provided as an external value (for example, if maintained in a database). It must be a numeric value, and when providing it, the **version_type** should be set to **external**. In this case, the check will be if the provided version is greater than the current document version. If so, it will be set as the document version value and the document will be indexed. If the current document version is higher than the provided version, a version conflict will be returned / thrown.


This means that async indexing as a result of operations done against the database can use the database versioning scheme and there is no need to maintain strict ordering in the async indexing process. Or even the simple case of updating the db, and then indexing into elasticsearch is now simplified since if the indexing gets out of order, the external versioning can be used to make sure only the latest version is indexed.


Operation Type
==============

The index operation also accepts an **op_type** to force a **create** operation. This will allow for a "put of absent" behavior when a document will be created only if it does not exists in the index.


Here is an example of using the **op_type** parameter:


.. code-block:: js

    $ curl -XPUT 'http://localhost:9200/twitter/tweet/1?op_type=create' -d '{
        "user" : "kimchy",
        "post_date" : "2009-11-15T14:12:12",
        "message" : "trying out Elastic Search"
    }'


Another option to specify **create** is to use the following uri:


.. code-block:: js

    $ curl -XPUT 'http://localhost:9200/twitter/tweet/1/_create' -d '{
        "user" : "kimchy",
        "post_date" : "2009-11-15T14:12:12",
        "message" : "trying out Elastic Search"
    }'



Automatic Id Generation
=======================

The index operation can be executed without specifying the id. In such a case, an id will be generated automatically for the document. In such a case, the **opType** will automatically be set to **create**. Here is an example (note the *POST* used instead of *PUT*):

.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/twitter/tweet/' -d '{
        "user" : "kimchy",
        "post_date" : "2009-11-15T14:12:12",
        "message" : "trying out Elastic Search"
    }'


The result of the above index operation is:


.. code-block:: js


    {
        "ok" : true,
        "_index" : "twitter",
        "_type" : "tweet",
        "_id" : "6a8ca01c-7896-48e9-81cc-9f70661fcb32"
    }


Routing
=======

When indexing documents, the document will end up being indexed into a specific shard. By default, the shard is controlled by hashing the id value of the document and using the hash value to control the shard it will end at. For more explicit control of the routing, one can be specified as part of the API call. For example:


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/twitter/tweet?routing=kimchy' -d '{
        "user" : "kimchy",
        "post_date" : "2009-11-15T14:12:12",
        "message" : "trying out Elastic Search"
    }'


The above sample will route the indexing of the tweet message based on the user name. Note, the **_routing** mapping option allows to control automatic extraction of the routing value from an indexed document without the need to explicitly set it at the cost of (very lightweight) additional parsing of the doc. Also, if the **_routing** mapping is defined, and set to be **required**, then the index operation will fail if no routing is provided (or extracted).


Parent
======

When indexing a child document, it is important that it will be routed to the same shard as the parent. This uses the routing capability. When indexing a doc with a parent id, it is automatically set as the routing value (unless the routing value is explicitly defined). Indexing a document with a parent id is simple:


.. code-block:: js

    $ curl -XPUT localhost:9200/blogs/blog_tag/1122?parent=1111 -d '{
        "tag" : "something"
    }'


Percolate
=========

:ref:`Percolation <es-guide-reference-api-percolate>`  can be automatically done on an indexed doc by passing the **percolate** parameter. Setting it to ***** will cause all percolation queries registered against the index to be checked against the indexed doc, for example:


.. code-block:: js

    curl -XPUT localhost:9200/test/type1/1?percolate=* -d '{
        "field1" : "value1"
    }'


It can also be set to query (following the query string syntax) to filter out which percolator queries will be executed:


.. code-block:: js

    curl -XPUT localhost:9200/test/type1/1?percolate=color:green -d '{
        "field1" : "value1",
        "field2" : "value2"
    }'


Percolation on index operation is done while optimizing the distributed nature of elasticsearch. Once the index operation is done on the primary shard, it is sent to all the replicas, and while the operation is done on the replicas, the percolation is executed on the node hosting the primary shard. Also, the parsing operation done on the primary shard is reused for the percolation operation.


Distributed
===========

The index operation gets hashed into a specific shard id. It then gets redirected into the primary shard within that id group, and replicated (if needed) to shard replicas within that id group.


Replication Type
================

The replication of the operation can be done in an asynchronous manner to the replicas (the operation will return once it has be executed on the primary shard). The **replication** parameter can be set to **async** (defaults to **sync**) in order to enable it.


Write Consistency
=================

Control if the operation will be allowed to execute based on the number of active shards within that partition (replication group). The values allowed are **one**, **quorum**, and **all**. The parameter to set it is **consistency**, and it defaults to the node level setting of **action.write_consistency** which in turn defaults to **quorum**.


For example, in a N shards with 2 replicas index, there will have to be at least 2 active shards within the relevant partition (**quorum**) for the operation to succeed. In a N shards with 1 replica scenario, there will need to be a single shard active (in this case, **one** and **quorum** is the same).


Refresh
=======

The **refresh** parameter can be set to **true** in order to refresh the relevant shard after the index operation has occurred and make it searchable. Setting it to **true** should be done after careful thought and verification that this does not cause a heavy load on the system (and slows down indexing).


Timeout
=======

The primary shard that needs to perform the operation might not be available yet. For example, it might still be in the process of recovery from a gateway, or might be in the process of relocation. The timeout parameter allows to control how long the index operation will wait till the primary shard is available before exiting with an error. The parameter name is **timeout** with a default value of 1 minute. Here is an example of setting it to 5 minutes:


.. code-block:: js

    $ curl -XPUT 'http://localhost:9200/twitter/tweet/1?timeout=5m' -d '{
        "user" : "kimchy",
        "post_date" : "2009-11-15T14:12:12",
        "message" : "trying out Elastic Search"
    }'


