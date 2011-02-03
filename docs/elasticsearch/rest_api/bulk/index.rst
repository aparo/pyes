Bulk
====

The bulk API allows to index and delete several documents in a single API. This can greatly increase the indexing speed.The REST API endpoint is /_bulk and it follows the following structure (for **json**):


.. code-block:: js

    action_and_meta_data\n
    optional_source\n
    action_and_meta_data\n
    optional_source\n
    ....
    action_and_meta_data\n
    optional_source\n


The json format relies on the fact that Json string values must have **\n** escaped, and that the actual json actions and sources are not pretty printed. Here is an example:


.. code-block:: js

    { "index" : { "_index" : "test", "_type" : "type1", "_id" : "1" } }
    { "type1" : { "field1" : "value1" } }
    { "delete" : { "_index" : "test", "_type" : "type1", "_id" : "2" } }
    { "create" : { "_index" : "test", "_type" : "type1", "_id" : "1" } }
    { "field1" : "value1" }
    


In the optional source part, the `type` is optional as is when indexing data.


A note on the format. The idea here is to make processing of this as fast as possible. As some of the actions will be needed to be redirected to other shards that exists on other nodes, only the action meta_data is parsed on the receiving node side. Also, zero copy buffers can be used on the source directly writing segments relevant to each action source to the network.


Client libraries using this protocol should try and strive to do something similar on the client side, and reduce as much as possible the creation of buffers.


The result is a full formatted json, with all the actions performed (in the same order), with possible error field indicating for each one in case of failure (on an item level).


Note, in the end, the full data needs to be represented on each server, so indexing 5GB of data should be broken down and not executed in a single batch.


If using the HTTP API, make sure that the client does not send HTTP chunks, as this will slow things down.


Routing
-------

Each bulk item can include the routing value using the **_routing** field. It automatically follows the behavior of the index / delete operation based on the **_routing** mapping.


Parent
------

Each bulk item can include the parent value using the **_parent** field. It automatically follows the behavior of the index / delete operation based on the **_parent** / **_routing** mapping.


Write Consistency
-----------------

Control if the operation will be allowed to execute based on the number of active shards within that partition (replication group). The values allowed are **one**, **quorum**, and **all**. The parameter to set it is **consistency**, and it defaults to the node level setting of **action.write_consistency** which in turn defaults to **quorum**.


For example, in a N shards with 2 replicas index, there will have to be at least 2 active shards within the relevant partition (**quorum**) for the operation to succeed. In a N shards with 1 replica scenario, there will need to be a single shard active (in this case, **one** and **quorum** is the same).


Refresh
-------

The **refresh** parameter can be set to **true** in order to refresh the relevant shards after the bulk operation has occurred and make it searchable. Setting it to **true** should be done after careful thought and verification that this does not cause a heavy load on the system (and slows down indexing).

