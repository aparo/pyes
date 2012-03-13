.. _es-guide-reference-api-delete:

======
Delete
======

The delete API allows to delete a typed JSON document from a specific index based on its id. The following example deletes the JSON document from an index called twitter, under a type called tweet, with id valued 1:


.. code-block:: js

    $ curl -XDELETE 'http://localhost:9200/twitter/tweet/1'


The result of the above delete operation is:


.. code-block:: js


    {
        "ok" : true,
        "_index" : "twitter",
        "_type" : "tweet",
        "_id" : "1",
        "found" : true
    }


Versioning
==========

Each document indexed is versioned. When deleting a document, the **version** can be specified to make sure the relevant document we are trying to delete is actually being deleted and it has not changed in the meantime.


Routing
=======

When indexing using the ability to control the routing, in order to delete a document, the routing value should also be provided. For example:


.. code-block:: js

    $ curl -XDELETE 'http://localhost:9200/twitter/tweet/1?routing=kimchy'


The above will delete a tweet with id 1, but will be routed based on the user. Note, issuing a delete without the correct routing, will cause the document to not be deleted.


Many times, the routing value is not known when deleting a document. For those cases, when specifying the **_routing** mapping as **required**, and no routing value is specified, the delete will be broadcasted automatically to all shards.


Parent
======

The **parent** parameter can be set, which will basically be the same as setting the routing parameter.


Note that deleting a parent document does not automatically delete its children. One way of deleting all child documents given a parent's id is to perform a :ref:`delete by query <es-guide-reference-api-delete-by-query>`  on the child index with the automatically generated (and indexed) field ==_parent==, which is in the format ==parent_type#parent_id==.


Automatic for the Index
=======================

The delete operation automatically creates an index if it has not been created before (check out the :ref:`create index API <es-guide-reference-api-admin-indices-create-index>`  for manually creating an index), and also automatically creates a dynamic type mapping for the specific type if it has not been created before (check out the :ref:`put mapping <es-guide-reference-api-admin-indices-put-mapping>`  API for manually creating type mapping). 


Distributed
===========

The delete operation gets hashed into a specific shard id. It then gets redirected into the primary shard within that id group, and replicated (if needed) to shard replicas within that id group.

Replication Type
================

The replication of the operation can be done in an asynchronous manner to the replicas (the operation will return once it has be executed on the primary shard). The **replication** parameter can be set to **async** (defaults to **sync**) in order to enable it.


Write Consistency
=================

Control if the operation will be allowed to execute based on the number of active shards within that partition (replication group). The values allowed are **one**, **quorum**, and **all**. The parameter to set it is **consistency**, and it defaults to the node level setting of **action.write_consistency** which in turn defaults to **quorum**.


For example, in a N shards with 2 replicas index, there will have to be at least 2 active shards within the relevant partition (**quorum**) for the operation to succeed. In a N shards with 1 replica scenario, there will need to be a single shard active (in this case, **one** and **quorum** is the same).


Refresh
=======

The **refresh** parameter can be set to **true** in order to refresh the relevant shard after the delete operation has occurred and make it searchable. Setting it to **true** should be done after careful thought and verification that this does not cause a heavy load on the system (and slows down indexing).

