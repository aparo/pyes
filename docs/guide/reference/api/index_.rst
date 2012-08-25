.. _es-guide-reference-api-index_:

======
Index_
======

The index API adds or updates a typed JSON document in a specific index, making it searchable. The following example inserts the JSON document into the "twitter" index, under a type called "tweet" with an id of 1:


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


Automatic Index Creation
========================

The index operation automatically creates an index if it has not been created before (check out the :ref:`create index API <es-guide-reference-api-admin-indices-create-index>`  for manually creating an index), and also automatically creates a dynamic type mapping for the specific type if one has not yet been created (check out the :ref:`put mapping <es-guide-reference-api-admin-indices-put-mapping>`  API for manually creating a type mapping).


The mapping itself is very flexible and is schema-free. New fields and objects will automatically be added to the mapping definition of the type specified. Check out the :ref:`mapping <es-guide-reference-mapping>`  section for more information on mapping definitions.


Though explained on the :ref:`mapping <es-guide-reference-mapping>`  section, its important to note that the format of the JSON document can also include the type (very handy when using JSON mappers), for example:


.. code-block:: js

    $ curl -XPUT 'http://localhost:9200/twitter/tweet/1' -d '{
        "tweet" : {
            "user" : "kimchy",
            "post_date" : "2009-11-15T14:12:12",
            "message" : "trying out Elastic Search"
        }
    }'


Automatic index creation can be disabled by setting **action.auto_create_index** to **false** in the config file of all nodes. Automatic mapping creation can be disabled by setting **index.mapper.dynamic** to **false** in the config files of all nodes (or on the specific index settings).


Versioning
==========

Each indexed document is given a version number. The associated **version** number is returned as part of the response to the index API request. The index API optionally allows for `optimistic concurrency control <http://en.wikipedia.org/wiki/Optimistic_concurrency_control>`_  when the **version** parameter is specified. This will control the version of the document the operation is intended to be executed against. A good example of a use case for versioning is performing a transactional read-then-update. Specifying a **version** from the document initially read ensures no changes have happened in the meantime (when reading in order to update, it is recommended to set **preference** to **_primary**). For example:


.. code-block:: js

    curl -XPUT 'localhost:9200/twitter/tweet/1?version=2' -d '{
        "message" : "elasticsearch now has versioning support, double cool!"
    }'


*NOTE:* versioning is completely real time, and is not affected by the near real time aspects of search operations. If no version is provided, then the operation is executed without any version checks.


By default, internal versioning is used that starts at 1 and increments with each update. Optionally, the version number can be supplemented with an external value (for example, if maintained in a database). To enable this functionality, **version_type** should be set to **external**. The value provided must be a numeric, long value greater than 0, and less than around 9.2e+18. When using the external version type, instead of checking for a matching version number, the system checks to see if the version number passed to the index request is greater than  the version of the currently stored document. If true, the document will be indexed and the new version number used. If the value provided is less than or equal to the stored document's version number, a version conflict will occur and the index operation will fail.


A nice side effect is that there is no need to maintain strict ordering of async indexing operations executed a result of changes to a source database, as long as version numbers from the source database are used. Even the simple case of updating the elasticsearch index using data from a database is simplified if external versioning is used, as only the latest version will be used if the index operations are out of order for whatever reason.


Operation Type
==============

The index operation also accepts an **op_type** that can be used to force a **create** operation, allowing for "put-if-absent" behavior. When **create** is used, the index operation will fail if a document by that id already exists in the index.


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



Automatic ID Generation
=======================

The index operation can be executed without specifying the id. In such a case, an id will be generated automatically. In addition, the **op_type** will automatically be set to **create**. Here is an example (note the *POST* used instead of *PUT*):

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

By default, shard placement &mdash; or **routing** &mdash; is controlled by using a hash of the document's id value. For more explicit control, the value fed into the hash function used by the router can be directly specified on a per-operation basis using the **routing** parameter. For example:


.. code-block:: js

    $ curl -XPOST 'http://localhost:9200/twitter/tweet?routing=kimchy' -d '{
        "user" : "kimchy",
        "post_date" : "2009-11-15T14:12:12",
        "message" : "trying out Elastic Search"
    }'


In the example above, the "tweet" document is routed to a shard based on the **routing** parameter provided: "kimchy".


When setting up explicit mapping, the **_routing** field can be optionally used to direct the index operation to extract the routing value from the document itself. This does come at the (very minimal) cost of an additional document parsing pass. If the **_routing** mapping is defined, and set to be **required**, the index operation will fail if no routing value is provided or extracted.


Parents &amp; Children
======================

A child document can be indexed by specifying it's parent when indexing. For example:


.. code-block:: js

    $ curl -XPUT localhost:9200/blogs/blog_tag/1122?parent=1111 -d '{
        "tag" : "something"
    }'


When indexing a child document, the routing value is automatically set to be the same as it's parent, unless the routing value is explicitly specified using the **routing** parameter.


Timestamp
=========

A document can be indexed with a **timestamp** associated with it. The **timestamp** value of a document can be set using the **timestamp** parameter. For example:


.. code-block:: js

    $ curl -XPUT localhost:9200/twitter/tweet/1?timestamp=2009-11-15T14%3A12%3A12 -d '{
        "user" : "kimchy",
        "message" : "trying out Elastic Search",
    }'


If the **timestamp** value is not provided externally or in the **_source**, the **timestamp** will be automatically set to the date the document was processed by the indexing chain. More information can be found on the :ref:`_timestamp mapping page <es-guide-reference-mapping-timestamp-field>`.

TTL
===

A document can be indexed with a **ttl** (time to live) associated with it. Expired documents will be expunged automatically. The expiration date that will be set for a document with a provided **ttl** is relative to the **timestamp** of the document, meaning it can be based on the time of indexing or on any time provided. The provided **ttl** must be strictly positive and can be a number (in milliseconds) or any valid time value as shown in the following examples:


.. code-block:: js

    curl -XPUT 'http://localhost:9200/twitter/tweet/1?ttl=86400000' -d '{
        "user": "kimchy",
        "message": "Trying out elasticsearch, so far so good?"
    }'


.. code-block:: js

    curl -XPUT 'http://localhost:9200/twitter/tweet/1?ttl=1d' -d '{
        "user": "kimchy",
        "message": "Trying out elasticsearch, so far so good?"
    }'


.. code-block:: js

    curl -XPUT 'http://localhost:9200/twitter/tweet/1' -d '{
        "_ttl": "1d",
        "user": "kimchy",
        "message": "Trying out elasticsearch, so far so good?"
    }'


More information can be found on the :ref:`_ttl mapping page <es-guide-reference-mapping-ttl-field>`.
Percolate
=========

:ref:`Percolation <es-guide-reference-api-percolate>`  can be performed at index time by passing the **percolate** parameter. Setting it to ***** will cause all percolation queries registered against the index to be checked against the provided document, for example:


.. code-block:: js

    curl -XPUT localhost:9200/test/type1/1?percolate=* -d '{
        "field1" : "value1"
    }'


To filter out which percolator queries will be executed, pass the query string syntax to the **percolate** parameter:


.. code-block:: js

    curl -XPUT localhost:9200/test/type1/1?percolate=color:green -d '{
        "field1" : "value1",
        "field2" : "value2"
    }'


*NOTE:* In a distributed cluster, percolation during the index operation is performed on the primary shard, as soon as the index operation completes. The operation executes on the primary while the replicas are updating, concurrently. Percolation during the index operation somewhat cuts down on parsing overhead, as the parse tree for the document is simply re-used for percolation.


Distributed
===========

The index operation is directed to the primary shard based on it's route (see the Routing section above) and performed on the actual node containing this shard. After the primary shard completes the operation, if needed, the update is distributed to applicable replicas.


Write Consistency
=================

To prevent writes from taking place on the "wrong" side of a network partition, by default, index operations only succeed if a quorum (>replicas/2+1) of active shards are available. This default can be overridden on a node-by-node basis using the **action.write_consistency** setting. To alter this behavior per-operation, the **consistency** request parameter can be used.


Valid write consistency values are **one**, **quorum**, and **all**.


Asynchronous Replication
========================

By default, the index operation only returns after all shards within the replication group have indexed the document (sync replication). To enable asynchronous replication, causing the replication process to take place in the background, set the **replication** parameter to **async**. When asynchronous replication is used, the index operation will return as soon as the operation succeeds on the primary shard.


Refresh
=======

To refresh the index immediately after the operation occurs, so that the document appears in search results immediately, the **refresh** parameter can be set to **true**. Setting this option to **true** should *ONLY* be done after careful thought and verification that it does not lead to poor performance, both from an indexing and a search standpoint. Note, getting a document using the get API is completely realtime.


Timeout
=======

The primary shard assigned to perform the index operation might not be available when the index operation is executed. Some reasons for this might be that the primary shard is currently recovering from a gateway or undergoing relocation. By default, the index operation will wait on the primary shard to become available for up to 1 minute before failing and responding with an error. The **timeout** parameter can be used to explicitly specify how long it waits. Here is an example of setting it to 5 minutes:


.. code-block:: js

    $ curl -XPUT 'http://localhost:9200/twitter/tweet/1?timeout=5m' -d '{
        "user" : "kimchy",
        "post_date" : "2009-11-15T14:12:12",
        "message" : "trying out Elastic Search"
    }'


